from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection


@add_metaclass(ABCMeta)
class AbstractSCPReceiver(AbstractConnection):
    """ A receiver of SCP messages
    """

    @abstractmethod
    def is_scp_receiver(self):
        pass

    @abstractmethod
    def receive_scp_response(self, scp_response, timeout=None):
        """ Receives an SCP message from this connection.  Blocks\
            until a message has been received, or a timeout occurs.
        
        :param scp_response: The response to fill in
        :rtype scp_response:\
                    :py:class:`spinnman.messages.scp.abstract_scp_response.AbstractSCPResponse`
        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid SCP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one\
                    of the fields of the SCP message is invalid
        """
