from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse

_LEVEL = 0
_APP_MASK = 0xFF
_ALL_CORE_MASK = 0xFFFF


def _get_arg_1(app_id, tag):
    data = ((_LEVEL & 3) | ((tag & 0xFF) << 8) | ((app_id & 0xFF) << 16) |
            (_APP_MASK << 24))
    return data


def _get_arg_2(states):
    wait_states = 0
    for state in states:
        wait_states |= (1 << state.value)
    return wait_states


class WaitForState(AbstractSCPRequest):
    """ An SCP Request to get a count of the cores in a particular state
    """
    __slots__ = []

    def __init__(self, app_id, states, tag):
        """

        :param app_id: The ID of the application, between 0 and 255
        :type app_id: int
        :param state: The state to count
        :type state: :py:class:`spinnman.model.cpu_state.CPUState`
        """
        super(WaitForState, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0,
                destination_chip_x=self.DEFAULT_DEST_X_COORD,
                destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_WAIT),
            argument_1=_get_arg_1(app_id, tag),
            argument_2=_get_arg_2(states),
            argument_3=_ALL_CORE_MASK)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Wait for state", SCPCommand.CMD_WAIT)
