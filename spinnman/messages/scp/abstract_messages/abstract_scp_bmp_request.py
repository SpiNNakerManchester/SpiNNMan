"""
AbstractSCPBMPRequest
"""

# spinnman imports
from spinnman.messages.scp.abstract_messages.abstract_scp_request import \
    AbstractSCPRequest


class AbstractSCPBMPRequest(AbstractSCPRequest):
    """
    represents a scp request thats tialored for the bmp connection
    """

    def __init__(
            self, sdp_header, scp_request_header, argument_1=None,
            argument_2=None, argument_3=None, data=None):
        AbstractSCPRequest.__init__(self, sdp_header, scp_request_header,
                                    argument_1, argument_2, argument_3, data)
