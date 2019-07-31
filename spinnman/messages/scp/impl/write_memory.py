# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinn_utilities.overrides import overrides
from spinnman.constants import address_length_dtype
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class WriteMemory(AbstractSCPRequest):
    """ A request to write memory on a chip
    """
    __slots__ = [
        "_data_to_write"]

    def __init__(self, x, y, base_address, data, cpu=0):
        """
        :param x: The x-coordinate of the chip, between 0 and 255;\
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255;\
            this is not checked due to speed restrictions
        :type y: int
        :param base_address: The base_address to start writing to \
            the base address is not checked to see if its not valid
        :type base_address: int
        :param data: between 1 and 256 bytes of data to write;\
            this is not checked due to speed restrictions
        :type data: bytearray or string
        """
        # pylint: disable=too-many-arguments
        size = len(data)
        super(WriteMemory, self).__init__(
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
        datastring = super(WriteMemory, self).bytestring
        return datastring + bytes(self._data_to_write)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("WriteMemory", "CMD_WRITE")
