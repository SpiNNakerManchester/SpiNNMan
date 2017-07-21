import struct

from .udp_connection import UDPConnection
from .utils import update_sdp_header_for_udp_send
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.scp.enums import SCPResult
from spinnman.connections.abstract_classes \
    import SCPReceiver, SCPSender


class BMPConnection(
        UDPConnection, SCPReceiver, SCPSender):
    """ A BMP connection which supports queries to the BMP of a SpiNNaker\
        machine
    """

    def __init__(self, cabinet, frame, boards, local_host=None,
                 local_port=None, remote_host=None,
                 remote_port=None):
        """
        :param cabinet: The cabinet number of the connection
        :type cabinet: int
        :param frame: The frame number of the connection
        :type frame: int
        :param boards: The boards that the connection can control on the same\
                backplane
        :type boards: iterable of int
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
        if remote_port is None:
            remote_port = SCP_SCAMP_PORT
        UDPConnection.__init__(
            self, local_host, local_port, remote_host, remote_port)
        SCPReceiver.__init__(self)
        SCPSender.__init__(self)
        self._cabinet = cabinet
        self._frame = frame
        self._boards = boards

    @property
    def cabinet(self):
        """ The cabinet id of the BMP

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """ The frame id of the BMP

        :rtype: int
        """
        return self._frame

    @property
    def boards(self):
        """ The set of boards supported by the BMP

        :rtype: iterable of int
        """
        return self._boards

    @property
    def chip_x(self):
        """ Defined to satisfy the SCPSender - always 0 for a BMP
        """
        return 0

    @property
    def chip_y(self):
        """ Defined to satisfy the SCPSender - always 0 for a BMP
        """
        return 0

    def get_scp_data(self, scp_request):
        update_sdp_header_for_udp_send(scp_request.sdp_header, 0, 0)
        return struct.pack("<2x") + scp_request.bytestring

    def receive_scp_response(self, timeout=1.0):
        data = self.receive(timeout)
        result, sequence = struct.unpack_from("<2H", data, 10)
        return SCPResult(result), sequence, data, 2

    def send_scp_request(self, scp_request):
        self.send(self.get_scp_data(scp_request))

    def __repr__(self):
        return \
            "BMPConnection(cabinet={}, frame={}, boards={}, local_host={},"\
            "local_port={}, remote_host={}, remote_port={}".format(
                self._cabinet, self._frame, self._boards,
                self.local_ip_address, self.local_port, self.remote_ip_address,
                self.remote_port)
