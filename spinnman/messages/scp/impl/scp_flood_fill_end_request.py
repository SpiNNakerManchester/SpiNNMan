from spinnman.messages.scp.abstract_messages.abstract_scp_request import AbstractSCPRequest
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.scp_command import SCPCommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse

_NNP_FORWARD_RETRY = (0x3f << 8) | 0x18
_NNP_FLOOD_FILL_END = 15


class SCPFloodFillEndRequest(AbstractSCPRequest):
    """ A request to start a flood fill of data
    """

    def __init__(self, nearest_neighbour_id, app_id=0, processors=None):
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
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the id is out of range
                    * If the app_id is out of range
                    * If one of the processors is out of range
                    * If only one of app_id or processors is specified
        """
        if nearest_neighbour_id < 0 or nearest_neighbour_id > 127:
            raise SpinnmanInvalidParameterException(
                    "nearest_neighbour_id", str(nearest_neighbour_id),
                    "Must be between 0 and 127")
        if ((app_id == 0 and processors is not None)
                or (app_id != 0 and processors is None)):
            raise SpinnmanInvalidParameterException(
                    "app_id and processors", "{} and {}".format(
                            app_id, processors),
                    "Both or neither of app_id and processors must be"
                    " specified")
        if app_id != 0 and (app_id < 16 or app_id > 255):
            raise SpinnmanInvalidParameterException(
                    "app_id", str(app_id), "Must be between 16 and 255")

        processor_mask = 0
        if processors is not None:
            for processor in processors:
                if processor < 1 or processor > 17:
                    raise SpinnmanInvalidParameterException(
                            "processors", str(processor),
                            "Each processor must be between 1 and 17")
                processor_mask |= (1 << processor)

        key = (_NNP_FLOOD_FILL_END << 24) | nearest_neighbour_id
        data = (app_id << 24) | processor_mask

        super(SCPFloodFillEndRequest, self).__init__(
                SDPHeader(flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                        destination_cpu=0, destination_chip_x=0,
                        destination_chip_y=0),
                SCPRequestHeader(command=SCPCommand.CMD_NNP),
                argument_1=key, argument_2=data, argument_3=_NNP_FORWARD_RETRY)

    def get_scp_response(self):
        return SCPCheckOKResponse("Flood Fill", "CMD_NNP:NNP_FFS")
