from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, AbstractSCPResponse
from spinnman.messages.scp.enums import SCPCommand, DPRICommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.model import DPRIStatus
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException


class DPRIGetStatus(AbstractSCPRequest):
    """ An SCP Request to get the status of the dropped packet reinjection
    """

    def __init__(self, x, y, p):
        """
        :param x: The x-coordinate of a chip, between 0 and 255
        :type x: int
        :param y: The y-coordinate of a chip, between 0 and 255
        :type y: int
        :param p: The processor running the dropped packet reinjector, between\
                0 and 17
        :type p: int
        """
        AbstractSCPRequest.__init__(
            self,
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=p, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_DPRI),
            argument_1=DPRICommand.GET_STATUS.value)

    def get_scp_response(self):
        return SCPDPRIGetStatusResponse()


class SCPDPRIGetStatusResponse(AbstractSCPResponse):
    """ An SCP response to a request for the dropped packet reinjection status
    """

    def __init__(self):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._dpri_status = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Get dropped packet reinjection status", SCPCommand.CMD_DPRI,
                result.name)
        self._dpri_status = DPRIStatus(data, offset)

    @property
    def dpri_status(self):
        return self._dpri_status
