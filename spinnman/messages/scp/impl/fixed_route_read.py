# Copyright (c) 2017 The University of Manchester
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
from typing import List
from spinn_utilities.overrides import overrides
from spinn_machine import RoutingEntry
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPHeader, SDPFlag

_ONE_WORD = struct.Struct("<I")


class _FixedRouteResponse(AbstractSCPResponse):
    """
    response for the fixed route read
    """
    __slots__ = [
        # the fixed route router entry
        "_route"]

    def __init__(self) -> None:
        super().__init__()
        self._route = 0

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read Fixed Route entry", "CMD_RTR", result.name)

        self._route = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def route(self) -> RoutingEntry:
        """ Converts this response into a Route """
        processor_ids: List[int] = list()
        for processor_id in range(26):
            if self._route & (1 << (6 + processor_id)) != 0:
                processor_ids.append(processor_id)
        link_ids: List[int] = list()
        for link_id in range(6):
            if self._route & (1 << link_id) != 0:
                link_ids.append(link_id)
        return RoutingEntry(processor_ids=processor_ids, link_ids=link_ids)


class FixedRouteRead(AbstractSCPRequest[_FixedRouteResponse]):
    """
    Gets a fixed route entry.
    """
    __slots__ = ()

    def __init__(self, x: int, y: int, app_id: int):
        """
        :param x: The x-coordinate of the chip, between 0 and 255,
            this is not checked due to speed restrictions
        :param y: The y-coordinate of the chip, between 0 and 255,
            this is not checked due to speed restrictions
        :param app_id:
            The ID of the application with which to associate the routes.
            If not specified, defaults to 0.
        :raise SpinnmanInvalidParameterException:
            * If x is out of range
            * If y is out of range
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=(app_id << 8) | 3, argument_2=1 << 31)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> _FixedRouteResponse:
        return _FixedRouteResponse()
