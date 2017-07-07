from spinnman.messages.sdp import SDPMessage, SDPFlag
from .udp_connection import UDPConnection
from .utils import update_sdp_header_for_udp_send
from spinnman.connections.abstract_classes \
    import SDPReceiver, SDPSender, Listenable

import struct


class SDPConnection(
        UDPConnection, SDPReceiver, SDPSender,
        Listenable):

    def __init__(self, chip_x=None, chip_y=None, local_host=None,
                 local_port=None, remote_host=None, remote_port=None):
        """
        :param chip_x: The optional x-coordinate of the chip at the remote\
                end of the connection.  If not specified, it will not be\
                possible to send SDP messages that require a response with\
                this connection.
        :type chip_x: int
        :param chip_y: The optional y-coordinate of the chip at the remote\
                end of the connection.  If not specified, it will not be\
                possible to send SDP messages that require a response with\
                this connection.
        :type chip_y: int
        :param local_host: The optional ip address or host name of the local\
                interface to listen on
        :type local_host: str
        :param local_port: The optional local port to listen on
        :type local_port: int
        :param remote_host: The optional remote host name or ip address to\
                send messages to.  If not specified, sending will not be\
                possible using this connection
        :type remote_host: str
        :param remote_port: The optional remote port number to send messages\
                to.  If not specified, sending will not be possible using this\
                connection
        """
        UDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)
        SDPReceiver.__init__(self)
        SDPSender.__init__(self)
        Listenable.__init__(self)
        self._chip_x = chip_x
        self._chip_y = chip_y

    def receive_sdp_message(self, timeout=None):
        data = self.receive(timeout)
        return SDPMessage.from_bytestring(data, 2)

    def send_sdp_message(self, sdp_message):

        # If a reply is expected, the connection should
        if sdp_message.sdp_header.flags == SDPFlag.REPLY_EXPECTED:
            update_sdp_header_for_udp_send(
                sdp_message.sdp_header, self._chip_x, self._chip_y)
        else:
            update_sdp_header_for_udp_send(sdp_message.sdp_header, 0, 0)
        self.send(struct.pack("<2x") + sdp_message.bytestring)

    def get_receive_method(self):
        return self.receive_sdp_message

    def __repr__(self):
        return \
            "SDPConnection(chip_x={}, chip_y={}, local_host={},"\
            " local_port={}, remote_host={}, remote_port={})".format(
                self._chip_x, self._chip_y, self.local_ip_address,
                self.local_port, self.remote_ip_address, self.remote_port)
