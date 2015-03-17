from spinnman.messages.scp.scp_signal import SCPSignal
from spinnman.messages.scp.abstract_messages.abstract_scp_request \
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_APP_MASK = 0xFF


def _get_data(app_id, signal):
    data = (_APP_MASK << 8) | app_id
    data += signal.value << 16
    return data


class SCPAppStopRequest(AbstractSCPRequest):
    """ An SCP Request to stop an application
    """

    def __init__(self, app_id):
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

        super(SCPAppStopRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=(0x3f << 16),
            argument_2=(5 << 28) | _get_data(app_id, SCPSignal.STOP),
            argument_3=(1 << 31) + (0x3f << 8))

    def get_scp_response(self):
        return SCPCheckOKResponse("Send Stop", "CMD_NNP")
