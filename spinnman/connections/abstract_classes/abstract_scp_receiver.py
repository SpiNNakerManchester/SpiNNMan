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
    def is_ready_to_receive(self):
        """ Determines if there is an SCP packet to be read without blocking

        :return: True if there is an SCP packet to be read
        :rtype: bool
        """
        pass

    @abstractmethod
    def receive_scp_response(self, timeout=1.0):
        """ Receives an SCP response from this connection.  Blocks\
            until a message has been received, or a timeout occurs.
        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: The SCP result, the sequence number, the data of the response\
                    and the offset at which the result starts (i.e. where the
                    SDP header starts)
        :rtype: (:py:class:`spinnman.messages.scp.scp_result.SCPResult`,\
                    int, bytestring, int)
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        """
