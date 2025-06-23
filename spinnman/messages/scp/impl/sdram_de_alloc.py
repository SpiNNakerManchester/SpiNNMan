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
from typing import Optional, overload
from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import AllocFree, SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_ONE_WORD = struct.Struct("<I")


class _SCPSDRAMDeAllocResponse(AbstractSCPResponse):
    """
    An SCP response to a request to deallocate SDRAM.
    """
    __slots__ = (
        "_number_of_blocks_freed",
        "_read_n_blocks_freed")

    def __init__(self, read_n_blocks_freed: bool = False):
        """
        """
        super().__init__()
        self._number_of_blocks_freed = 0
        self._read_n_blocks_freed = read_n_blocks_freed

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM deallocation", "CMD_DEALLOC", result.name)
        if self._read_n_blocks_freed:
            self._number_of_blocks_freed = _ONE_WORD.unpack_from(
                data, offset)[0]

            # check that the base address is not null (0 in python case) as
            # this reflects a issue in command on SpiNNaker side
            if self._number_of_blocks_freed == 0:
                raise SpinnmanUnexpectedResponseCodeException(
                    "SDRAM deallocation response base address", "CMD_DEALLOC",
                    result.name)

    @property
    def number_of_blocks_freed(self) -> int:
        """
        The number of allocated blocks that have been freed from the
        app_id given.
        """
        return self._number_of_blocks_freed


class SDRAMDeAlloc(AbstractSCPRequest[_SCPSDRAMDeAllocResponse]):
    """
    An SCP Request to free space in the SDRAM.
    """
    __slots__ = "_read_n_blocks_freed",

    @overload
    def __init__(self, x: int, y: int, *, app_id: int,
                 base_address: None = None):
        ...

    @overload
    def __init__(self, x: int, y: int, *, app_id: None = None,
                 base_address: int):
        ...

    def __init__(self, x: int, y: int, *, app_id: Optional[int] = None,
                 base_address: Optional[int] = None):
        """
        :param x:
            The x-coordinate of the chip to allocate on, between 0 and 255
        :param y:
            The y-coordinate of the chip to allocate on, between 0 and 255
        :param app_id: The ID of the application, between 0 and 255
        :param base_address: The start address in SDRAM to which the block
            needs to be deallocated, or `None` if deallocating via app_id
        """
        if base_address is not None:
            assert app_id is None
            super().__init__(
                SDPHeader(
                    flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
                argument_1=(
                    AllocFree.
                    FREE_SDRAM_BY_POINTER.value),
                argument_2=base_address)
            self._read_n_blocks_freed = False
        else:
            assert app_id is not None
            super().__init__(
                SDPHeader(
                    flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
                argument_1=(
                    app_id << 8 |
                    AllocFree.
                    FREE_SDRAM_BY_APP_ID.value))
            self._read_n_blocks_freed = True

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> _SCPSDRAMDeAllocResponse:
        return _SCPSDRAMDeAllocResponse(self._read_n_blocks_freed)
