from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection


@add_metaclass(AbstractBase)
class AbstractSpinnakerBootSender(AbstractConnection):
    """ A sender of Spinnaker Boot messages
    """

    __slots__ = ()

    @abstractmethod
    def send_boot_message(self, boot_message):
        """ Sends a SpiNNaker boot message using this connection

        :param boot_message: The message to be sent
        :type boot_message:\
                    :py:class:`spinnman.messages.spinnaker_boot.spinnaker_boot_message.SpinnakerBootMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        pass
