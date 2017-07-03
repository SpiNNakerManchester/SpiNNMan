from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand, Signal
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_APP_MASK = 0xFF


def _get_data(app_id, signal):
    data = (_APP_MASK << 8) | app_id
    data += signal.value << 16
    return data


class AppStop(AbstractSCPRequest):
    """ An SCP Request to stop an application
    """

    def __init__(self, app_id):
        """

        :param app_id: The id of the application, between 0 and 255
        :type app_id: int
        """
        super(AppStop, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=(0x3f << 16),
            argument_2=(5 << 28) | _get_data(app_id, Signal.STOP),
            argument_3=(1 << 31) + (0x3f << 8))

    def get_scp_response(self):
        return CheckOKResponse("Send Stop", "CMD_NNP")
