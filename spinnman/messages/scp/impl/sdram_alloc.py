# Copyright (c) 2015 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import struct
from typing import Optional
from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import AllocFree, SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import (
    SpinnmanUnexpectedResponseCodeException, SpinnmanInvalidParameterException)

_ONE_WORD = struct.Struct("<I")

FLAG_RETRY_TAG = 4


class _AllocResponse(AbstractSCPResponse):
    """
    An SCP response to a request to allocate space in SDRAM.
    """
    __slots__ = (
        "_base_address",
        "_size")

    def __init__(self, size: int):
        """
        :param size: The size in bytes of memory to be allocated
        """
        super().__init__()
        self._size = size
        self._base_address: Optional[int] = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM Allocation", "CMD_ALLOC", result.name)
        self._base_address = _ONE_WORD.unpack_from(data, offset)[0]

        # check that the base address is not null (0 in python case) as
        # this reflects a issue in the command on SpiNNaker side
        if self._base_address == 0:
            raise SpinnmanInvalidParameterException(
                "SDRAM Allocation response base address", self._base_address,
                f"Could not allocate {self._size} bytes of SDRAM")

    @property
    def base_address(self) -> int:
        """
        The base address allocated, or 0 if none.
        """
        return self._base_address or 0


class SDRAMAlloc(AbstractSCPRequest[_AllocResponse]):
    """
    An SCP Request to allocate space in the SDRAM space.
    """
    __slots__ = "_size",

    def __init__(self, x: int, y: int, app_id: int, size: int,
                 tag: Optional[int] = None, retry_tag: bool = True):
        """
        :param x:
            The x-coordinate of the chip to allocate on, between 0 and 255
        :param y:
            The y-coordinate of the chip to allocate on, between 0 and 255
        :param app_id: The ID of the application, between 0 and 255
        :param size: The size in bytes of memory to be allocated
        :param tag:
            The tag for the SDRAM, a 8-bit (chip-wide) tag that can be
            looked up by a SpiNNaker application to discover the address of
            the allocated block. If `0` then no tag is applied.
        :param retry_tag:
            If a tag is used, add a safety check to retry the tag.  This can
            avoid issues with re-allocating memory on a retry message.
        """
        extra_flag = 0
        if retry_tag and tag is not None:
            extra_flag = FLAG_RETRY_TAG

        if tag is None:
            tag = 0
        elif not (0 <= tag < 256):
            raise SpinnmanInvalidParameterException(
                "tag",
                "The tag param needs to be between 0 and 255, or None (in "
                "which case 0 will be used by default)", str(tag))

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (extra_flag << 16) |
                (app_id << 8) |
                AllocFree.ALLOC_SDRAM.value),
            argument_2=size, argument_3=tag)
        self._size = size

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> _AllocResponse:
        return _AllocResponse(self._size)
