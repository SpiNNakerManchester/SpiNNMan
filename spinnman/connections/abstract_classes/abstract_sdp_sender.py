from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_connection import AbstractConnection
from spinnman.data.little_endian_byte_array_byte_writer import \
    LittleEndianByteArrayByteWriter
from spinnman.exceptions import SpinnmanIOException
from spinnman.messages.udp_utils import udp_utils as utils


@add_metaclass(ABCMeta)
class AbstractSDPSender(AbstractConnection):
    """ A sender of SDP messages
    """
    
    @abstractmethod
    def is_sdp_sender(self):
        pass

    @abstractmethod
    def send_sdp_message(self, sdp_message):
        """ Sends an SDP message down this connection
        
        :param sdp_message: The SDP message to be sent
        :type sdp_message: spinnman.messages.sdp.sdp_message.SDPMessage
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """