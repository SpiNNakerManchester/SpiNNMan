from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_connection import AbstractConnection

@add_metaclass(ABCMeta)
class AbstractSpinnakerBootSender(AbstractConnection):
    """ A sender of Spinnaker Boot messages
    """
    
    @abstractmethod
    def send_boot_message(self, boot_message):
        """ Sends a SpiNNaker boot message using this connection
        
        :param boot: The message to be sent
        :type boot_message: spinnman.messages.spinnaker_boot_message.SpinnakerBootMessage
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        pass
