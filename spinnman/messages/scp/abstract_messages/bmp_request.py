"""
BMPRequest
"""

# spinnman imports
from .scp_request import AbstractSCPRequest
from spinnman.messages.sdp import SDPFlag, SDPHeader


class BMPRequest(AbstractSCPRequest):
    """ An SCP request intended to be sent to a BMP
    """

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

        sdp_header = SDPHeader(
            flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
            destination_cpu=BMPRequest.get_first_board(boards),
            destination_chip_x=0, destination_chip_y=0)
        AbstractSCPRequest.__init__(self, sdp_header, scp_request_header,
                                    argument_1, argument_2, argument_3, data)

    @staticmethod
    def get_first_board(boards):
        """ Get the first board id given an int or iterable of ints
        """
        if isinstance(boards, int):
            return boards
        return boards[0]

    @staticmethod
    def get_board_mask(boards):
        """ Get the board mask given an int or iterable of ints of board ids
        """
        if isinstance(boards, int):
            return 1 << boards
        return sum(1 << board for board in boards)
