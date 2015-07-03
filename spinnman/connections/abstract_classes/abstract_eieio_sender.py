from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass
from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection


@add_metaclass(ABCMeta)
class AbstractEIEIOSender(AbstractConnection):
    """ A sender of EIEIO messages
    """

    @abstractmethod
    def send_eieio_message(self, eieio_message):
        """ Sends an EIEIO message down this connection

        :param eieio_message: The eieio message to be sent
        :type eieio_message: \
                    :py:class:`spinnman.messages.eieio.abstract_messages.abstract_eieio_message.AbstractEIEIOMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
