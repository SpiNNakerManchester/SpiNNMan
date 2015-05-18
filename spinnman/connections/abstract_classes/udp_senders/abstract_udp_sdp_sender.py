from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

import struct

from spinnman.connections.abstract_classes.abstract_connection \
    import AbstractConnection
from spinnman.connections.abstract_classes.udp_senders import udp_utils
from spinnman.exceptions import SpinnmanIOException


@add_metaclass(ABCMeta)
class AbstractUDPSDPSender(AbstractConnection):
    """ A sender of SDP messages
    """

    @abstractmethod
    def is_udp_sdp_sender(self):
        pass

    def send_sdp_message(self, sdp_message):
        if not self._can_send:
            raise SpinnmanIOException("Not connected to a remote host")

        # Update the SDP headers for this connection
        udp_utils.update_sdp_header_for_udp_send(sdp_message.sdp_header)

        # Send the packet
        try:
            self._socket.send(struct.pack("<2x") + sdp_message.bytestring)
        except Exception as e:
            raise SpinnmanIOException(str(e))
