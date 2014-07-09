__author__ = 'Petrut'

import unittest
import spinnman.connections.udp_connection as udp_conn
import spinnman.messages.scp_message as scp_msg
import spinnman.messages.sdp_message as sdp_msg
import unittests.udp_connection as hack_udp
import unittests.virtual_spinnaker as virtual_spinnaker

class TestUDPConnection(unittest.TestCase):

    def setUp(self):
        self.vs = virtual_spinnaker.VirtualSpiNNaker('localhost',17893)
        self.udp = hack_udp.UDPConnection('localhost',17893)

    def tearDown(self):
        self.vs.close()
        self.udp.close()

    def test_setup_new_udp_connection(self):
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "192.16.240.253"
        remoteport = 12345
        connection = udp_conn.UDPConnection(localhost,localport, remotehost)

        self.assertEqual(connection.local_ip_address, localhost)
        self.assertEqual(connection.local_port,localport)

    def test_send_scp_message_with_confirmation(self):
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "127.0.0.1"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport, remotehost)
        msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_EXPECTED,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,bytearray(0))

        connection.send_scp_message(msg)
        response = connection.receive_scp_message()
        #TODO -> Have to manually build an SCP packet and check against the one created by the constructor of SCPMessage
        #TODO -> Add test checking the translation was succesful in Virtual SpiNNaker and the response is appropriate
        self.assertEqual(True,False)

    def test_send_scp_message_without_confirmation(self):
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "127.0.0.1"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport, remotehost)
        msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,bytearray(0))
        connection.send_scp_message(msg)

        #TODO -> Have to manually build an SCP packet and check against the one created by the constructor of SCPMessage
        #TODO -> Add test checking the translation was succesful in Virtual SpiNNaker


    def test_send_non_wrapped_scp_message_with_confirmation(self):
        #TODO -> Have to manually build an SCP packet and check against the one created by the constructor of SCPMessage
        self.assertEqual(True,False)

    def test_send_non_wrapped_scp_message_without_confirmation(self):
        #TODO -> Have to manually build an SCP packet and check against the one created by the constructor of SCPMessage
        self.assertEqual(True,False)

    def test_send_sdp_message_with_confirmation(self):
        self.assertEqual(True,False)

    def test_send_sdp_message_without_confirmation(self):
        self.assertEqual(True,False)

    def test_send_boot_message(self):
        self.assertEqual(True,False)

    def test_receive_boot_message(self):
        self.assertEqual(True,False)

    def test_receive_scp_message(self):
        self.assertEqual(True,False)

    def test_receive_sdp_message(self):
        self.assertEqual(True,False)

    def test_send_message_with_low_timeout(self):
        self.assertEqual(True,False)

    '''
    def test_virtual_spinnaker_basic_message(self):
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "127.0.0.1"
        remoteport = 12345
        connection = udp_conn.UDPConnection(localhost,localport, remotehost)
    '''

    def test_send_scp_message_to_inexistent_host(self):
        with self.assertRaises(Exception):
            localhost = "127.0.0.1"
            localport = 54321
            remotehost = "127.0.0.1"
            remoteport = 61616
            connection = udp_conn.UDPConnection(localhost,localport, remotehost)
            msg = scp_msg.SCPMessage(sdp_msg.Flag.REPLY_NOT_EXPECTED,0,1,0,0,0,1,0,0,0,scp_msg.Command.CMD_APLX,0,1,2,3,bytearray(0))
            connection.send_scp_message(msg)


if __name__ == '__main__':
    unittest.main()
