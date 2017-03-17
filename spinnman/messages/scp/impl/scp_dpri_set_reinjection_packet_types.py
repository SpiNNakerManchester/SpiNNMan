from spinnman.messages.scp.abstract_messages.abstract_scp_request\
    import AbstractSCPRequest
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.sdp.sdp_flag import SDPFlag
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.enums.scp_command import SCPCommand
from spinnman.messages.scp.enums.scp_dpri_command import SCPDPRICommand
from spinnman.messages.scp.impl.scp_check_ok_response import SCPCheckOKResponse


class SCPDPRISetReinjectionPacketTypesRequest(AbstractSCPRequest):
    """ An SCP Request to set the dropped packet reinjected packet types
    """

    def __init__(self, x, y, p, packet_types):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param p: The processor running the dropped packet reinjector, between\
                0 and 17
        :type p: int
        :param packet_types: The types of packet to reinject - if empty or\
                None reinjection is disabled
        :type packet_types: None or list of \
                `py:class:spinnman.messages.scp.scp_dpri_packet_type_flags.SCPDPRIPacketTypeFlags`
        """
        flags = 0
        if packet_types is not None:
            for packet_type in packet_types:
                flags |= packet_type.value

        AbstractSCPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=p, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_DPRI),
            argument_1=SCPDPRICommand.SET_PACKET_TYPES.value,
            argument_2=flags)

    def get_scp_response(self):
        return SCPCheckOKResponse("Set reinjected packet types",
                                  SCPCommand.CMD_DPRI)
