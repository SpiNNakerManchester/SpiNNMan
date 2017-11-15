from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp.impl import CheckOKResponse
from spinnman.messages.sdp import SDPHeader, SDPFlag


class FixedRouteInit(AbstractSCPRequest):

    def __init__(self, x, y, entry, app_id):
        """ sets a fixed route entry

        :param x: The x-coordinate of the chip, between 0 and 255, \
        this is not checked due to speed restrictions
        :type x: int
        :param y: The y-coordinate of the chip, between 0 and 255\
        this is not checked due to speed restrictions
        :type y: int
        :param entry: the fixed route entry converted for writing
        :param app_id: The id of the application with which to associate the\
                    routes.  If not specified, defaults to 0.
        :type app_id: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:\
                    * If x is out of range
                    * If y is out of range
        """

        AbstractSCPRequest.__init__(
            self, SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=(app_id << 8) | 3, argument_2=entry)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("RouterInit", "CMD_RTR")
