from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_ALL_CORE_MASK = 0xFFFF
_APP_MASK = 0xFF


def _get_data(app_id, signal):
    data = (_APP_MASK << 8) | app_id
    data += signal.value << 16
    return data


class SendSignal(AbstractSCPRequest):
    """ An SCP Request to send a signal to cores
    """

    def __init__(self, app_id, signal):
        """

        :param app_id: The id of the application, between 0 and 255
        :type app_id: int
        :param signal: The signal to send
        :type signal: :py:class:`spinnman.messages.scp.scp_signal.SCPSignal`
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If\
            app_id is out of range
        """

        if app_id < 0 or app_id > 255:
            raise SpinnmanInvalidParameterException(
                "app_id", str(app_id), "Must be between 0 and 255")

        super(SendSignal, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_SIG),
            argument_1=signal.signal_type.value,
            argument_2=_get_data(app_id, signal),
            argument_3=_ALL_CORE_MASK)

    def get_scp_response(self):
        return CheckOKResponse("Send Signal", "CMD_SIG")
