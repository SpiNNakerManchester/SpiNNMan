from six import add_metaclass

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class SDPReceiver(Connection):
    """ A receiver of SDP messages
    """

    __slots__ = ()

    @abstractmethod
    def receive_sdp_message(self, timeout=None):
        """ Receives an SDP message from this connection.  Blocks until the\
            message has been received, or a timeout occurs.

        :param timeout: The time in seconds to wait for the message to arrive;\
                    if not specified, will wait forever, or until the\
                    connection is closed
        :type timeout: int
        :return: The received SDP message
        :rtype: :py:class:`spinnman.messages.sdp.sdp_message.SDPMessage`
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    receiving the message
        :raise spinnman.exceptions.SpinnmanTimeoutException: If there is a\
                    timeout before a message is received
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If the\
                    received packet is not a valid SDP message
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If one \
                    of the fields of the SDP message is invalid
        """
