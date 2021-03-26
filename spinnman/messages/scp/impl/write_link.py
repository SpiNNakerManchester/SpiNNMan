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
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class WriteLink(AbstractSCPRequest):
    """ A request to write memory on a neighbouring chip
    """
    __slots__ = [
        "_data_to_write"]

    def __init__(self, x, y, link, base_address, data, cpu=0):
        """
        :param int x: The x-coordinate of the chip whose neighbour will be
            written to, between 0 and 255
        :param int y: The y-coordinate of the chip whose neighbour will be
            written to, between 0 and 255
        :param int cpu: The CPU core to use, normally 0
            (or if a BMP, the board slot number)
        :param int link: The link number to write to between 0 and 5
            (or if a BMP, the FPGA between 0 and 2)
        :param int base_address: The base_address to start writing to
        :param bytes data: Up to 256 bytes of data to write
        """
        # pylint: disable=too-many-arguments
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_LINK_WRITE),
            argument_1=base_address, argument_2=len(data), argument_3=link,
            data=None)
        self._data_to_write = data

    @property
    def bytestring(self):
        return super().bytestring + bytes(self._data_to_write)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("WriteMemory", "CMD_WRITE")
