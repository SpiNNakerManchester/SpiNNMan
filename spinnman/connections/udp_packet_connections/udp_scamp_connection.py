from spinnman import constants
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.connections.udp_packet_connections import udp_utils
from spinnman.connections.udp_packet_connections.udp_sdp_connection \
    import UDPSDPConnection
from spinnman.connections.abstract_classes.abstract_scp_sender \
    import AbstractSCPSender
from spinnman.connections.abstract_classes.abstract_scp_receiver \
    import AbstractSCPReceiver

import struct


class UDPSCAMPConnection(UDPSDPConnection, AbstractSCPSender,
                         AbstractSCPReceiver):
    """ A UDP connection to SCAMP on the board
    """

    def __init__(self, chip_x=0, chip_y=0, local_host=None, local_port=None,
                 remote_host=None, remote_port=constants.SCP_SCAMP_PORT):
        """

        :param chip_x: The x-coordinate of the chip on the board with this\
                remote_host
        :type chip_x: int
        :param chip_y: The y-coordinate of the chip on the board with this\
                remote_host
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
        :type remote_port: int
        """
        UDPSDPConnection.__init__(
            self, chip_x, chip_y, local_host, local_port, remote_host,
            remote_port)
        AbstractSCPReceiver.__init__(self)
        AbstractSCPSender.__init__(self)

    @property
    def chip_x(self):
        return self._chip_x

    @property
    def chip_y(self):
        return self._chip_y

    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = struct.unpack_from("<2H", data, 10)
        return SCPResult(result), sequence, data, 2

    def send_scp_request(self, scp_request):
        udp_utils.update_sdp_header_for_udp_send(scp_request.sdp_header, 0, 0)
        self.send(struct.pack("<2x") + scp_request.bytestring)
