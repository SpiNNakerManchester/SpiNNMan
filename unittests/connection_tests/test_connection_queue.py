import unittest
import spinnman.connections.udp_connection as udp_conn
from spinnman.connections.udp_boot_connection import UDPBootConnection
import spinnman.connections._connection_queue as c_q
from spinnman.messages.sdp.sdp_message import SDPMessage
from spinnman.messages.sdp.sdp_header import SDPHeader
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.scp.scp_request_header import SCPRequestHeader
from spinnman.messages.scp.impl.scp_version_request import SCPVersionRequest
from spinnman.messages.multicast_message import MulticastMessage
from spinnman.messages.spinnaker_boot.spinnaker_boot_op_code import SpinnakerBootOpCode
from spinnman.messages.spinnaker_boot.spinnaker_boot_message import SpinnakerBootMessage
from spinnman.connections.udp_boot_connection import UDPBootConnection
from threading import Condition

class TestConnectionQueue(unittest.TestCase):
    def test_creating_new_connection_queue(self):
        remotehost = "192.168.240.253"
        connection = udp_conn.UDPConnection(remote_host= remotehost)
        connection2 = UDPBootConnection(remote_host=remotehost)
        conn_queue = c_q._ConnectionQueue(connection)

        self.assertEqual(conn_queue._connection,connection)
        self.assertFalse(conn_queue._done)
        self.assertEqual(conn_queue.queue_length, 0)

    def test_check_message_type_sdp(self):
        remotehost = "192.168.240.253"
        connection = udp_conn.UDPConnection(remote_host= remotehost)
        conn_queue = c_q._ConnectionQueue(connection)
        header = SDPHeader()
        msg = SDPMessage(header)
        self.assertTrue(conn_queue.message_type_supported(msg, False))

    def test_check_message_type_sdp_response(self):
        remotehost = "192.168.240.253"
        connection = udp_conn.UDPConnection(remote_host= remotehost)
        conn_queue = c_q._ConnectionQueue(connection)
        header = SDPHeader()
        msg = SDPMessage(header)
        self.assertTrue(conn_queue.message_type_supported(msg, True))

    def test_check_message_type_scp(self):
        remotehost = "192.168.240.253"
        connection = udp_conn.UDPConnection(remote_host= remotehost)
        conn_queue = c_q._ConnectionQueue(connection)
        header = SCPVersionRequest(0,0,0)
        self.assertTrue(conn_queue.message_type_supported(header, True))

    def test_check_message_type_scp_no_response(self):
        remotehost = "192.168.240.253"
        connection = udp_conn.UDPConnection(remote_host= remotehost)
        conn_queue = c_q._ConnectionQueue(connection)
        header = SCPVersionRequest(0,0,0)
        self.assertTrue(conn_queue.message_type_supported(header, False))

    def test_check_message_type_multicast(self):
        # remotehost = "192.168.240.253"
        # connection = udp_conn.UDPConnection(remote_host= remotehost)
        # conn_queue = c_q._ConnectionQueue(connection)
        # header = MulticastMessage(10)
        # self.assertTrue(conn_queue.message_type_supported(header, False))
        self.assertEqual("Check type multicast", True)


    def test_check_message_type_boot(self):
        # remotehost = "192.168.240.253"
        # connection = udp_conn.UDPConnection(remote_host= remotehost)
        # conn_queue = c_q._ConnectionQueue(connection)
        # header = UDPBootConnection(remote_host= remotehost)
        # msg = SpinnakerBootMessage(SpinnakerBootOpCode.FLOOD_FILL_BLOCK,None,None, None)
        # self.assertTrue(conn_queue.message_type_supported(msg, False))
        self.assertEqual("Check type boot message", True)


    def test_check_message_type_not_supported(self):
        with self.assertRaises(SpinnmanInvalidPacketException):
            remotehost = "192.168.240.253"
            connection = udp_conn.UDPConnection(remote_host= remotehost)
            conn_queue = c_q._ConnectionQueue(connection)
            header = SDPHeader()
            msg = SDPMessage(header)
            conn_queue.message_type_supported("someMessage", True)

if __name__ == '__main__':
    unittest.main()
