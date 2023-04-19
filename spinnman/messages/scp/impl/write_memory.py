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
from spinnman.constants import address_length_dtype
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class WriteMemory(AbstractSCPRequest):
    """
    A request to write memory on a chip.
    """
    __slots__ = [
        "_data_to_write"]

    def __init__(self, x, y, base_address, data, cpu=0):
        """
        :param int x: The x-coordinate of the chip, between 0 and 255;
            this is not checked due to speed restrictions
        :param int y: The y-coordinate of the chip, between 0 and 255;
            this is not checked due to speed restrictions
        :param int base_address: The base_address to start writing to
            the base address is not checked to see if its not valid
        :param data: between 1 and 256 bytes of data to write;
            this is not checked due to speed restrictions
        :type data: bytearray or bytes
        """
        # pylint: disable=too-many-arguments
        size = len(data)
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_WRITE),
            argument_1=base_address, argument_2=size,
            argument_3=address_length_dtype[
                (base_address % 4), (size % 4)].value,
            data=None)
        self._data_to_write = data

    @property
    def bytestring(self):
        return super().bytestring + bytes(self._data_to_write)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("WriteMemory", "CMD_WRITE")
