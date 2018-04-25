from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class SpinnakerBootSender(Connection):
    """ A sender of SpiNNaker Boot messages
    """

    __slots__ = ()

    @abstractmethod
    def send_boot_message(self, boot_message):
        """ Sends a SpiNNaker boot message using this connection.

        :param boot_message: The message to be sent
        :type boot_message:\
            :py:class:`spinnman.messages.spinnaker_boot.SpinnakerBootMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error sending the message
        """
