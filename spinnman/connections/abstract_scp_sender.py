from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_connection import AbstractConnection

@add_metaclass(ABCMeta)
class AbstractSCPSender(AbstractConnection):
    """ A sender of SCP messages
    """
    
    @abstractmethod
    def send_scp_message(self, scp_message):
        """ Sends an SCP message down this connection
        
        :param message: message packet to send
        :type message: spinnman.messages.scp_message.SCPMessage
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        pass
