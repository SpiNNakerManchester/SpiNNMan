# spinnman imports
from spinnman.messages.scp.abstract_messages import BMPRequest
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from .get_version_response import GetVersionResponse
from spinnman.messages.scp.abstract_messages.scp_request import AbstractSCPRequest
from spinn_utilities.overrides import overrides


class BMPGetVersion(BMPRequest):
    """ An SCP request to read the version of software running on a core
    """

    def __init__(self, board):
        """
        :param board: The board to get the version from
        :type board: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
            * If the chip coordinates are out of range
            * If the processor is out of range
        """
        super(BMPGetVersion, self).__init__(
            board, SCPRequestHeader(command=SCPCommand.CMD_VER))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return GetVersionResponse()
