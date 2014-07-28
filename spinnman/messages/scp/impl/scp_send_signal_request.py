from spinnman.messages.scp.abstract_messages.abstract_scp_request \
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_ALL_CORE_MASK = 0xFFFF
_APP_MASK = 0xFF


def _get_data(app_id, signal):
    data = (_APP_MASK << 8) | app_id
    data += signal.value << 16
    return data


class SCPSendSignalRequest(AbstractSCPRequest):
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

        super(SCPSendSignalRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_SIG),
            argument_1=signal.signal_type,
            argument_2=_get_data(app_id, signal),
            argument_3=_ALL_CORE_MASK)

    def get_scp_response(self):
        return SCPCheckOKResponse("Send Signal", "CMD_SIG")
