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
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class RouterInit(AbstractSCPRequest):
    """ A request to initialize the router on a chip
    """
    __slots__ = []

    def __init__(self, x, y, n_entries, table_address, base_address, app_id):
        """
        :param x: The x-coordinate of the chip, between 0 and 255,\
            this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255,\
            this is not checked due to speed restrictions
        :type y: int
        :param n_entries: The number of entries in the table, more than 0
        :type n_entries: int
        :param table_address: The allocated table address
        :type table_address: int
        :param base_address: The base_address containing the entries
        :type base_address: int
        :param app_id: The ID of the application with which to associate the\
            routes.  If not specified, defaults to 0.
        :type app_id: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
            * If x is out of range
            * If y is out of range
            * If n_entries is 0 or less
            * If table_address is not positive
            * If base_address is not positive
        """
        # pylint: disable=too-many-arguments
        if n_entries < 1:
            raise SpinnmanInvalidParameterException(
                "n_entries", str(n_entries), "Must be more than 0")
        if base_address < 0:
            raise SpinnmanInvalidParameterException(
                "base_address", str(base_address),
                "Must be a positive integer")
        if table_address < 0:
            raise SpinnmanInvalidParameterException(
                "table_address", str(table_address),
                "Must be a positive integer")

        super(RouterInit, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=((n_entries << 16) | (app_id << 8) | 2),
            argument_2=table_address, argument_3=base_address)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("RouterInit", "CMD_RTR")
