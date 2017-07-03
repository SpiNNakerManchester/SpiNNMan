from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.messages.sdp import SDPHeader
from spinnman.messages.scp import SCPResponseHeader

# The offset of the header from the start of a received packet
# (8 bytes of SDP header)
_SCP_HEADER_OFFSET = 8

# The offset of the data from the start of a received packet
# (8 bytes of SDP header + 4 bytes of SCP header)
_SCP_DATA_OFFSET = 12


@add_metaclass(AbstractBase)
class AbstractSCPResponse(object):
    """ Represents an abstract SCP Response
    """

    def __init__(self):
        """
        """
        self._sdp_header = None
        self._scp_response_header = None

    def read_bytestring(self, data, offset):
        """ Reads a packet from a bytestring of data

        :param data: The bytestring to be read
        :type data: str
        :param offset: The offset in the data from which the response should\
                    be read
        :type offset: int
        """
        self._sdp_header = SDPHeader.from_bytestring(data, offset)
        self._scp_response_header = SCPResponseHeader.from_bytestring(
            data, _SCP_HEADER_OFFSET + offset)
        self.read_data_bytestring(data, _SCP_DATA_OFFSET + offset)

    @abstractmethod
    def read_data_bytestring(self, data, offset):
        """ Reads the remainder of the data following the header

        :param data: The bytestring to read from
        :type data: str
        :param offset: The offset into the data after the headers
        :type offset: int
        """
        pass

    @property
    def sdp_header(self):
        """ The SDP header from the response

        :return: The SDP header
        :rtype: :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :raise None: No known exceptions are raised
        """
        return self._sdp_header

    @property
    def scp_response_header(self):
        """ The SCP header from the response

        :return: The SCP header
        :rtype:\
                    :py:class:`spinnman.messages.scp.scp_response_header.SCPResponseHeader`
        :raise None: No known exceptions are raised
        """
        return self._scp_response_header
