from spinnman import constants
import struct

from spinnman.messages.scp.enums.scp_result import SCPResult
from spinnman.connections.udp_packet_connections import udp_utils
from spinnman.connections.udp_packet_connections.udp_sdp_connection \
    import UDPSDPConnection
from spinnman.connections.abstract_classes.abstract_scp_sender \
    import AbstractSCPSender
from spinnman.connections.abstract_classes.abstract_scp_receiver \
    import AbstractSCPReceiver


class UDPSCAMPConnection(UDPSDPConnection, AbstractSCPSender,
                         AbstractSCPReceiver):
    """ A UDP connection to SCAMP on the board
    """

    def __init__(
            self, chip_x=255, chip_y=255, local_host=None, local_port=None,
            remote_host=None, remote_port=None):
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
        if remote_port is None:
            remote_port = constants.SCP_SCAMP_PORT
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

    def update_chip_coordinates(self, x, y):
        self._chip_x = x
        self._chip_y = y

    def get_scp_data(self, scp_request):
        udp_utils.update_sdp_header_for_udp_send(scp_request.sdp_header,
                                                 self._chip_x, self._chip_y)
        return struct.pack("<2x") + scp_request.bytestring

    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = struct.unpack_from("<2H", data, 10)
        return SCPResult(result), sequence, data, 2

    def send_scp_request(self, scp_request):
        self.send(self.get_scp_data(scp_request))

    def __repr__(self):
        return \
            "UDPSCAMPConnection(chip_x={}, chip_y={}, local_host={}," \
            " local_port={}, remote_host={}, remote_port={})".format(
                self._chip_x, self._chip_y, self.local_ip_address,
                self.local_port, self.remote_ip_address, self.remote_port)
