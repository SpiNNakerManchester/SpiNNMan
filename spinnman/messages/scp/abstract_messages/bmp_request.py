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

from typing import Generic, Iterable, Optional, TypeVar, Union
from typing_extensions import TypeAlias

from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp import SCPRequestHeader

from .bmp_response import BMPResponse
from .scp_request import AbstractSCPRequest

#: The type of boards parameters.
Boards: TypeAlias = Union[int, Iterable[int]]
R = TypeVar("R", bound=BMPResponse)


class BMPRequest(  # pylint: disable=abstract-method
        AbstractSCPRequest[R], Generic[R]):
    """
    An SCP request intended to be sent to a BMP.
    """
    __slots__ = ()

    def __init__(self, boards: Boards,
                 scp_request_header: SCPRequestHeader,
                 argument_1: Optional[int] = None,
                 argument_2: Optional[int] = None,
                 argument_3: Optional[int] = None,
                 data: Optional[bytes] = None):
        """
        :param boards: The board or boards to be addressed by this request
        :param scp_request_header: The SCP request header
        :param argument_1: The optional first argument
        :param argument_2: The optional second argument
        :param argument_3: The optional third argument
        :param data: The optional data to be sent
        """
        sdp_header = SDPHeader(
            flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
            destination_cpu=BMPRequest.get_first_board(boards),
            destination_chip_x=0, destination_chip_y=0)
        super().__init__(
            sdp_header, scp_request_header,
            argument_1, argument_2, argument_3, data)

    @staticmethod
    def get_first_board(boards: Boards) -> int:
        """
        :returns:
           The first board ID given a board ID or collection of board IDs.
        """
        if isinstance(boards, int):
            return boards
        return min(boards)

    @staticmethod
    def get_board_mask(boards: Boards) -> int:
        """
        Get the board mask given a board ID or collection of board IDs.

        ..note:: This methods is only called by deprecated functions.
           Unsure if it will produce the correct result for multiple boards

        :returns: The board ID as a bit mask,
           or a sum of bitmaps for multiple boards
        """
        if isinstance(boards, int):
            return 1 << boards
        return sum(1 << board for board in boards)
