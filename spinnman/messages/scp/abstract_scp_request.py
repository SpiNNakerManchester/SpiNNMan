from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class AbstractSCPRequest(object):
    """ Represents an Abstract SCP Request
    """
    
    def __init__(self, sdp_header, scp_request_header, data=None):
        """
        
        :param sdp_header: The SDP header of the request
        :type sdp_header:\
                    :py:class:`spinnman.messages.sdp.sdp_header.SDPHeader`
        :param scp_request_header: The SCP header of the request
        :type scp_request_header:\
                    :py:class:`spinnman.messages.scp.scp_request_header.SCPRequestHeader`
        :raise None: No known exceptions are raised
        """
        self._sdp_header = sdp_header
        self._scp_request_header = scp_request_header
        
    @property
    def sdp_header(self):
        """ The SDP header of the message
        
        :rtype: :py:class:`spinnman.message.sdp.sdp_header.SDPHeader`
        """
        return self._sdp_header
    
    @property
    def scp_request_header(self):
        """ The SCP request header of the message
        
        :rtype: :py:class:`spinnman.messages.scp.scp_request_header.SCPRequestHeader`
        """
        return self._scp_request_header
    
    @abstractmethod
    def write_scp_request(self, byte_writer):
        """ Write the scp request to the given writer
        
        :param byte_writer: The writer to write to
        :type byte_writer:\
                    :py:class:`spinnman.data.abstract_byte_writer.AbstractByteWriter`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    writing the request
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If any\
                    required values have not been set
        """
        self._sdp_header.write_sdp_header(byte_writer)
        self._scp_request_header.write_scp_request_header(byte_writer)
        
    @abstractmethod
    def get_scp_response(self):
        """ Get an SCP response message to be used to process any response\
            received
        
        :return: An SCP response, or None if no response is required
        :rtype: :py:class:`spinnman.messages.scp_response.SCPResponse`
        :raise None: No known exceptions are raised
        """
        pass
