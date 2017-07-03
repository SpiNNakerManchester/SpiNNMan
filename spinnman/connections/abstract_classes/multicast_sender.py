from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class MulticastSender(Connection):
    """ A sender of Multicast messages
    """

    __slots__ = ()

    @abstractmethod
    def get_input_chips(self):
        """ Get a list of chips which identify the chips to which this sender\
            can send multicast packets directly

        :return: An iterable of tuples of (x, y) where x is the x-coordinate\
                    of the chip and y is the y-coordinate of the chip
        :rtype: iterable of (int, int)
        :raise None: No known exceptions are raised
        """
        pass

    @abstractmethod
    def send_multicast_message(self, multicast_message):
        """ Sends a SpiNNaker multicast message using this connection

        :param multicast_message: The message to be sent
        :type multicast_message:\
                    :py:class:`spinnman.messages.multicast_message.MulticastMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
        pass
