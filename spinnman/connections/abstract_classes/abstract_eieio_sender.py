from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection
from spinn_utilities.abstract_base import AbstractBase, abstractmethod


@add_metaclass(AbstractBase)
class AbstractEIEIOSender(AbstractConnection):
    """ A sender of EIEIO messages
    """

    __slots__ = ()

    @abstractmethod
    def send_eieio_message(self, eieio_message):
        """ Sends an EIEIO message down this connection

        :param eieio_message: The eieio message to be sent
        :type eieio_message: \
                    :py:class:`spinnman.messages.eieio.abstract_messages.abstract_eieio_message.AbstractEIEIOMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
