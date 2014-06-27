from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_connection import AbstractConnection

@add_metaclass(ABCMeta)
class AbstractSDPReceiver(AbstractConnection):
    """ A receiver of SDP messages
    """
    
    @abstractmethod
    def receive_sdp_message(self, timeout=None):
        """ Receives an SDP message from this connection.  Blocks until the\
            message has been received, or a timeout occurs.
            
        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: The received SDP message
        :rtype: spinnman.messages.sdp_message.SDPMessage
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid SDP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one of\
                    the fields of the SDP message is invalid
        """
        pass
