from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass
from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection


@add_metaclass(ABCMeta)
class AbstractEIEIOSender(AbstractConnection):
    """ A receiver of SCP messages
    """

    @abstractmethod
    def is_eieio_sender(self):
        pass

    @abstractmethod
    def send_eieio_message(self, eieio_message):
        """ Sends an SDP message down this connection

        :param eieio_message: The eieio message to be sent
        :type eieio_message: \
                    :py:class:`spinnman.messages.eieio.eieio_data_message.EIEIODataMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    sending the message
        """
