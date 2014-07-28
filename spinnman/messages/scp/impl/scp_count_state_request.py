from spinnman.messages.scp.abstract_messages.abstract_scp_request \
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_count_state_response import \
    SCPCountStateResponse
from spinnman.exceptions import SpinnmanInvalidParameterException

_ALL_CORE_MASK = 0xFFFF
_COUNT_OPERATION = 1
_COUNT_MODE = 2
_COUNT_SIGNAL_TYPE = 1
_APP_MASK = 0xFF


def _get_data(app_id, state):
    data = (_APP_MASK << 8) | app_id
    data += (_COUNT_OPERATION << 22) | (_COUNT_MODE << 20)
    data += state.value << 16
    return data


class SCPCountStateRequest(AbstractSCPRequest):
    """ An SCP Request to get a count of the cores in a particular state
    """

    def __init__(self, app_id, state):
        """

        :param app_id: The id of the application, between 0 and 255
        :type app_id: int
        :param state: The state to count
        :type state: :py:class:`spinnman.model.cpu_state.CPUState`
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If\
            app_id is out of range
        """

        if app_id < 0 or app_id > 255:
            raise SpinnmanInvalidParameterException(
                "app_id", str(app_id), "Must be between 0 and 255")

        super(SCPCountStateRequest, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=0,
                destination_chip_y=0),
            SCPRequestHeader(command=SCPCommand.CMD_SIG),
            argument_1=_COUNT_SIGNAL_TYPE,
            argument_2=_get_data(app_id, state),
            argument_3=_ALL_CORE_MASK)

    def get_scp_response(self):
        return SCPCountStateResponse()
