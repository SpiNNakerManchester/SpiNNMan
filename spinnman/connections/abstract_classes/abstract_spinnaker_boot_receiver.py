from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_connection import AbstractConnection


@add_metaclass(ABCMeta)
class AbstractSpinnakerBootReceiver(AbstractConnection):
    """ A receiver of Spinnaker boot messages
    """
    
    @abstractmethod
    def receive_boot_message(self, timeout=None):
        """ Receives a boot message from this connection.  Blocks\
            until a message has been received, or a timeout occurs.
        
        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: a boot message
        :rtype: :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid spinnaker boot message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the spinnaker boot message is invalid
        """
        pass
