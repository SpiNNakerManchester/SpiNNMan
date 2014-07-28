from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.messages.scp.scp_response_header import SCPResponseHeader


@add_metaclass(ABCMeta)
class AbstractSCPResponse(object):
    """ Represents an abstract SCP Response
    """

    def __init__(self):
        """
        """
        self._sdp_header = SDPHeader()
        self._scp_response_header = SCPResponseHeader()

    @abstractmethod
    def read_scp_response(self, byte_reader):
        """ Read the scp response from the given reader

        :param byte_reader: The reader to read from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If there\
                    are not enough bytes to read the header
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        :raise spinnman.exceptions.SpinnmanUnexpectedResponseCodeException: If\
                    the response code indicates an error
        """
        self._sdp_header.read_sdp_header(byte_reader)
        self._scp_response_header.read_scp_response_header(byte_reader)

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
        :rtype: :py:class:`spinnman.messages.scp.scp_response_header.SCPResponseHeader`
        :raise None: No known exceptions are raised
        """
        return self._scp_response_header
