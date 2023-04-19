# Copyright (c) 2015 The University of Manchester
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

from .scp_request import AbstractSCPRequest
from spinnman.messages.sdp import SDPFlag, SDPHeader


class BMPRequest(AbstractSCPRequest):
    """
    An SCP request intended to be sent to a BMP.
    """
    __slots__ = []

    def __init__(self, boards, scp_request_header, argument_1=None,
                 argument_2=None, argument_3=None, data=None):
        """
        :param boards: The board or boards to be addressed by this request
        :type boards: int or list(int) or tuple(int)
        :param SCPRequestHeader scp_request_header: The SCP request header
        :param int argument_1: The optional first argument
        :param int argument_2: The optional second argument
        :param int argument_3: The optional third argument
        :param bytes data: The optional data to be sent
        """
        # pylint: disable=too-many-arguments
        sdp_header = SDPHeader(
            flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
            destination_cpu=BMPRequest.get_first_board(boards),
            destination_chip_x=0, destination_chip_y=0)
        super().__init__(
            sdp_header, scp_request_header,
            argument_1, argument_2, argument_3, data)

    @staticmethod
    def get_first_board(boards):
        """
        Get the first board ID given a board ID or collection of board IDs.
        """
        if isinstance(boards, int):
            return boards
        return min(boards)

    @staticmethod
    def get_board_mask(boards):
        """
        Get the board mask given a board ID or collection of board IDs.
        """
        if isinstance(boards, int):
            return 1 << boards
        return sum(1 << board for board in boards)
