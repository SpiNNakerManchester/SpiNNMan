from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import SCPCheckOKResponse

_NNP_FORWARD_RETRY = (0x3f << 8) | 0x18
_NNP_FLOOD_FILL_END = 15
_WAIT_FLAG = 0x1 << 18


class SCPFloodFillEndRequest(AbstractSCPRequest):
    """ A request to start a flood fill of data
    """

    def __init__(
            self, nearest_neighbour_id, app_id=0, processors=None, wait=False):
        """

        :param nearest_neighbour_id: The id of the packet, between 0 and 127
        :type nearest_neighbour_id: int
        :param app_id: The application id to start using the data, between 16\
                    and 255.  If not specified, no application is started
        :type app_id: int
        :param processors: A list of processors on which to start the\
                    application, each between 1 and 17.  If not specified,\
                    no application is started.
        :type processors: iterable of int
        :param wait: True if the binary should go into a "wait" state before\
                    executing
        :type wait: bool
        """
        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        key = (_NNP_FLOOD_FILL_END << 24) | nearest_neighbour_id
        data = (app_id << 24) | processor_mask
        if wait:
            data = data | _WAIT_FLAG

        super(SCPFloodFillEndRequest, self).__init__(
            SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                      destination_cpu=0,
                      destination_chip_x=self.DEFAULT_DEST_X_COORD,
                      destination_chip_y=self.DEFAULT_DEST_Y_COORD),
            SCPRequestHeader(command=SCPCommand.CMD_NNP),
            argument_1=key, argument_2=data, argument_3=_NNP_FORWARD_RETRY)

    def get_scp_response(self):
        return SCPCheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")