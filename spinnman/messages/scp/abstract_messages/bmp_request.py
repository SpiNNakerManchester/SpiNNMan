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

from .scp_request import AbstractSCPRequest
from spinnman.messages.sdp import SDPFlag, SDPHeader


class BMPRequest(AbstractSCPRequest):
    """ An SCP request intended to be sent to a BMP.
    """
    __slots__ = []

    def __init__(self, boards, scp_request_header, argument_1=None,
                 argument_2=None, argument_3=None, data=None):
        """
        :param boards: The board or boards to be addressed by this request
        :type boards: int or iterable of int
        :param scp_request_header: The SCP request header
        :param argument_1: The optional first argument
        :param argument_2: The optional second argument
        :param argument_3: The optional third argument
        :param data: The optional data to be sent
        """
        # pylint: disable=too-many-arguments
        sdp_header = SDPHeader(
            flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
            destination_cpu=BMPRequest.get_first_board(boards),
            destination_chip_x=0, destination_chip_y=0)
        super(BMPRequest, self).__init__(
            sdp_header, scp_request_header,
            argument_1, argument_2, argument_3, data)

    @staticmethod
    def get_first_board(boards):
        """ Get the first board ID given a board ID or collection of board IDs
        """
        if isinstance(boards, int):
            return boards
        return min(boards)

    @staticmethod
    def get_board_mask(boards):
        """ Get the board mask given a board ID or collection of board IDs
        """
        if isinstance(boards, int):
            return 1 << boards
        return sum(1 << board for board in boards)
