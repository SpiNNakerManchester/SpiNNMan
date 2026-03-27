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
from spinn_utilities.typing.coords import XYP
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.constants import address_length_dtype


class Response(AbstractSCPResponse):
    """
    An SCP response to a request to read a region of memory on a chip.
    """
    __slots__ = (
        "_data",
        "_length",
        "_offset",
        "__op",
        "__cmd")

    def __init__(self, operation: str, command: str) -> None:
        """
        :param operation: Operation name
        :param command: Command used for which this is the response
        """
        super().__init__()
        self._data = b''
        self._length = 0
        self._offset = 0
        self.__op = operation
        self.__cmd = command

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        assert self._scp_response_header is not None
        if self._scp_response_header.result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                self.__op, self.__cmd, self._scp_response_header.result)
        self._data = data
        self._offset = offset
        self._length = len(data) - offset

    @property
    def data(self) -> bytes:
        """
        The data read.

        .. note::
            The data starts at offset.
        """
        return self._data

    @property
    def offset(self) -> int:
        """
        The offset where the valid data starts.
        """
        return self._offset

    @property
    def length(self) -> int:
        """
        The length of the valid data.
        """
        return self._length


class ReadMemory(AbstractSCPRequest[Response]):
    """
    An SCP request to read a region of memory on a chip.
    """
    __slots__ = ()

    def __init__(self, coordinates: XYP, base_address: int, size: int):
        """
        :param coordinates:
            The X,Y,P coordinates of the chip to read from;
            X and Y between 0 and 255, P between 0 and 17
        :param base_address:
            The positive base address to start the read from
        :param size: The number of bytes to read, between 1 and 256
        :raise SpinnmanInvalidParameterException:
            * If the chip coordinates are out of range
            * If the base address is not a positive number
            * If the size is out of range
        """
        x, y, cpu = coordinates
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_READ),
            argument_1=base_address, argument_2=size,
            argument_3=address_length_dtype[
                (base_address % 4, size % 4)].value)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> Response:
        return Response("read memory", "CMD_READ")
