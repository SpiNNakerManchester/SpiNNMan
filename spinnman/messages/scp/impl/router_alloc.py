# Copyright (c) 2014 The University of Manchester
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
from spinnman.messages.scp.enums import (
    AllocFree, SCPCommand, SCPResult)
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_ONE_WORD = struct.Struct("<I")


class RouterAllocResponse(AbstractSCPResponse):
    """
    An SCP response to a request to allocate router entries.
    """
    __slots__ = "_base_address",

    def __init__(self) -> None:
        super().__init__()
        self._base_address: Optional[int] = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Router Allocation", "CMD_ALLOC", result.name)
        self._base_address = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def base_address(self) -> int:
        """
        The base address allocated, or 0 if none.
        """
        return self._base_address or 0


class RouterAlloc(AbstractSCPRequest[RouterAllocResponse]):
    """
    An SCP Request to allocate space for routing entries.
    """
    __slots__ = ()

    def __init__(self, x: int, y: int, app_id: int, n_entries: int):
        """
        :param x:
            The x-coordinate of the chip to allocate on, between 0 and 255
        :param y:
            The y-coordinate of the chip to allocate on, between 0 and 255
        :param app_id: The ID of the application, between 0 and 255
        :param n_entries: The number of entries to allocate
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (app_id << 8) |
                AllocFree.ALLOC_ROUTING.value),
            argument_2=n_entries)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> RouterAllocResponse:
        return RouterAllocResponse()
