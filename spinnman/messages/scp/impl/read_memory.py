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
from spinnman.constants import address_length_dtype


class ReadMemory(AbstractSCPRequest):
    """
    An SCP request to read a region of memory on a chip.
    """
    __slots__ = []

    def __init__(self, x, y, base_address, size, cpu=0):
        """
        :param int x:
            The x-coordinate of the chip to read from, between 0 and 255
        :param int y:
            The y-coordinate of the chip to read from, between 0 and 255
        :param int base_address:
            The positive base address to start the read from
        :param int size: The number of bytes to read, between 1 and 256
        :raise SpinnmanInvalidParameterException:
            * If the chip coordinates are out of range
            * If the base address is not a positive number
            * If the size is out of range
        """
        # pylint: disable=too-many-arguments
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
    def get_scp_response(self):
        return _SCPReadMemoryResponse()


class _SCPReadMemoryResponse(AbstractSCPResponse):
    """
    An SCP response to a request to read a region of memory on a chip.
    """
    __slots__ = [
        "_data",
        "_length",
        "_offset"]

    def __init__(self):
        super().__init__()
        self._data = None
        self._length = None
        self._offset = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        if self._scp_response_header.result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read", "CMD_READ", self._scp_response_header.result)
        self._data = data
        self._offset = offset
        self._length = len(data) - offset

    @property
    def data(self):
        """
        The data read.

        .. note::
            The data starts at offset.

        :rtype: bytearray
        """
        return self._data

    @property
    def offset(self):
        """
        The offset where the valid data starts.

        :rtype: int
        """
        return self._offset

    @property
    def length(self):
        """
        The length of the valid data.

        :rtype: int
        """
        return self._length
