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

from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class _SCPReadLinkResponse(AbstractSCPResponse):
    """
    An SCP response to a request to read a region of memory via a link on
    a chip.
    """
    __slots__ = (
        "_data",
        "_length",
        "_offset")

    def __init__(self) -> None:
        super().__init__()
        self._data = b''
        self._offset = 0
        self._length = 0

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "ReadLink", "CMD_READ_LINK", result.name)
        self._data = data
        self._offset = offset
        self._length = len(data) - offset

    @property
    def data(self) -> bytes:
        """
        The data read.

        :rtype: bytes
        """
        return self._data

    @property
    def offset(self) -> int:
        """
        The offset where the valid data starts.

        :rtype: int
        """
        return self._offset

    @property
    def length(self) -> int:
        """
        The length of the valid data.

        :rtype: int
        """
        return self._length


class ReadLink(AbstractSCPRequest[_SCPReadLinkResponse]):
    """
    An SCP request to read a region of memory via a link on a chip.
    """
    __slots__ = ()

    def __init__(self, x: int, y: int, link: int, base_address: int,
                 size: int, cpu: int = 0):
        """
        :param int x:
            The x-coordinate of the chip to read from, between 0 and 255
        :param int y:
            The y-coordinate of the chip to read from, between 0 and 255
        :param int link: The ID of the link down which to send the query
        :param int base_address:
            The positive base address to start the read from
        :param int size: The number of bytes to read, between 1 and 256
        :param int cpu:
            The CPU core to use, normally 0
            (or if a BMP, the board slot number)
        """
        # pylint: disable=too-many-arguments
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LINK_READ),
            argument_1=base_address, argument_2=size, argument_3=link)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> _SCPReadLinkResponse:
        return _SCPReadLinkResponse()
