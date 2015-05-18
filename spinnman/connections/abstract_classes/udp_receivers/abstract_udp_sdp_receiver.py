from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import socket

from spinnman.connections.abstract_classes.abstract_sdp_receiver import \
    AbstractSDPReceiver
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import SpinnmanIOException


@add_metaclass(ABCMeta)
class AbstractUDPSDPReceiver(AbstractSDPReceiver):
    """ A receiver of SDP messages
    """
    @abstractmethod
    def is_udp_sdp_reciever(self):
        pass

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
        """
        # Receive the data
        raw_data = None
        try:
            self._socket.settimeout(timeout)
            raw_data = self._socket.recv(512)
        except socket.timeout:
            raise SpinnmanTimeoutException("receive_sdp_message", timeout)
        except Exception as e:
            raise SpinnmanIOException(str(e))

        message = SDPMessage()
        message.read_bytestring(raw_data, 2)
        return message
