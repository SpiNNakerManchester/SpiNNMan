from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages \
    import AbstractSCPRequest, AbstractSCPResponse
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ChipSummaryInfo


class SCPChipInfoRequest(AbstractSCPRequest):
    """ An SCP request to read the chip information from a core
    """

    def __init__(self, x, y, with_size=False):
        """

        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param with_size: True if the size should be included in the response,\
                    False if not
        :type with_size: bool
        """
        # Bits 0-4 + bit 6 = all information except size
        argument_1 = 0x5F
        if with_size:

            # Bits 0-6 = all information including size
            argument_1 = 0x7F

        AbstractSCPRequest.__init__(
            self, SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_INFO),
            argument_1=argument_1)

    def get_scp_response(self):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_request.AbstractSCPRequest.get_scp_response`
        """
        return _SCPChipInfoResponse()


class _SCPChipInfoResponse(AbstractSCPResponse):
    """ An SCP response to a request for the version of software running
    """

    def __init__(self):
        """
        """
        AbstractSCPResponse.__init__(self)
        self._chip_info = None

    def read_data_bytestring(self, data, offset):
        """ See\
            :py:meth:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse.read_data_bytestring`
        """
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Version", "CMD_CHIP_INFO", result.name)
        self._chip_info = ChipSummaryInfo(
            data, offset, self.sdp_header.source_chip_x,
            self.sdp_header.source_chip_y,)

    @property
    def chip_info(self):
        """ The chip information received

        :rtype: :py:class:`spinnman.model.chip_summary_info.ChipSummaryInfo`
        """
        return self._chip_info
