__author__ = 'Petrut'

import unittest
import spinnman.connections.udp_connection as udp_conn
import spinnman.messages.scp_message as scp_msg
import spinnman.messages.sdp_message as sdp_msg
import unittests.udp_connection as hack_udp
import unittests.virtual_spinnaker as virtual_spinnaker
import spinnman.exceptions as exc
import spinnman.messages.sdp_flag as flags
import spinnman.messages.scp_command as cmds
import time
import thread

class TestUDPConnection(unittest.TestCase):

    # def setUp(self):
    #     #TODO ---> Run vSpiNNaker on a different thread and don't forget to run receive_message()
    #     #self.vs = virtual_spinnaker.VirtualSpiNNakerMessageReader('1','Virtual Spinnaker Threaded Message Reader',
    #     #                                                          1,)
    #
    #     self.vs = virtual_spinnaker.VirtualSpiNNaker('localhost',17893)
    #     thread.start_new_thread(self.vs.receive_message,())
    #     #self.vs.receive_message()
    #     #self.vs.run()
    #     self.udp = hack_udp.UDPConnection('localhost',17893)

    def tearDown(self):
        # self.vs.close()
        # self.udp.close()
        time.sleep(2)

    def test_setup_new_udp_connection(self):
        #self.udp = hack_udp.UDPConnection('localhost',17893)
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "127.0.0.1"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport, remotehost,remoteport)

        self.assertEqual(connection.local_ip_address, localhost)
        self.assertEqual(connection.local_port,localport)

    def test_send_scp_message_with_confirmation(self):
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "127.0.0.1"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport,remote_host = remotehost,remote_port= remoteport)
        msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3, 0)

        connection.send_scp_message(msg)
        response = connection.receive_scp_message(2)

        #self.assertEqual(response.flags,flags.SDPFlag.REPLY_NOT_EXPECTED)
        self.assertEqual(response.argument_1,1)
        self.assertEqual(response.argument_2,2)
        self.assertEqual(response.argument_3,3)
        self.assertEqual(response.command,cmds.SCPCommand.CMD_APLX.value)
        self.assertEqual(response.tag,0)
        self.assertEqual(response.destination_port,1)
        self.assertEqual(response.source_port,7)
        self.assertEqual(response.destination_chip_x,0)
        self.assertEqual(response.destination_chip_y,0)
        self.assertEqual(response.source_chip_x,0)
        self.assertEqual(response.source_chip_y,0)
        self.assertEqual(response.destination_cpu,0)
        self.assertEqual(response.source_cpu,31)
        self.assertEqual(response.sequence,0)

    def test_send_random_scp_msg_to_booted_spinnaker_board_with_confirmation(self):
        localhost = "192.168.240.254"
        localport = 54321
        remotehost = "192.168.240.253"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport,remote_host = remotehost,remote_port= remoteport)
        msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3, 0)

        connection.send_scp_message(msg)
        response = connection.receive_scp_message(2)


    def test_send_random_scp_msg_to_booted_spinnaker_board_without_confirmation(self):
        with self.assertRaises(Exception):
            localhost = "192.168.240.254"
            localport = 54321
            remotehost = "192.168.240.253"
            remoteport = 17893
            connection = udp_conn.UDPConnection(localhost,localport,remote_host = remotehost,remote_port= remoteport)
            msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3, 0)

            connection.send_scp_message(msg)
            response = connection.receive_scp_message(2)

    def test_send_scp_message_without_confirmation(self):
        localhost = "127.0.0.1"
        localport = 54321
        remotehost = "127.0.0.1"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport, remotehost,remoteport)
        msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3,0, 0, 7, 0,0,
                                  31, bytearray(0))
        connection.send_scp_message(msg)

    def test_send_cmd_ver_to_spinnaker_board(self):
        localhost = "192.168.240.254"
        localport = 54321
        remotehost = "192.168.240.253"
        remoteport = 17893
        connection = udp_conn.UDPConnection(localhost,localport,remote_host = remotehost,remote_port= remoteport)
        msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_VER, 1, 2, 3, 0)

        connection.send_scp_message(msg)
        response = connection.receive_scp_message(2)
        self.assertEquals(response.command,cmds.SCPCommand.CMD_APLX.value)
    # def test_send_sdp_message_with_confirmation(self):
    #     self.assertEqual(True,False)
    #
    # def test_send_sdp_message_without_confirmation(self):
    #     self.assertEqual(True,False)
    #
    # def test_send_boot_message(self):
    #     self.assertEqual(True,False)
    #
    # def test_receive_boot_message(self):
    #     self.assertEqual(True,False)
    #
    # def test_receive_scp_message(self):
    #     self.assertEqual(True,False)
    #
    # def test_receive_sdp_message(self):
    #     self.assertEqual(True,False)
    #
    # def test_send_message_with_low_timeout(self):
    #     self.assertEqual(True,False)

    def test_create_connection_without_remote_host(self):
        with self.assertRaises(exc.SpinnmanIOException):
            localhost = "127.0.0.1"
            localport = 54321
            remotehost = "127.0.0.1"
            remoteport = 12345
            connection = udp_conn.UDPConnection(localhost,localport)
            msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3,0, 0, 7, 0,0,
                                  31, bytearray(0))
            connection.send_scp_message(msg)

    def test_send_scp_message_to_inexistent_host(self):
        with self.assertRaises(exc.SpinnmanIOException):
            localhost = "127.0.0.1"
            localport = 54321
            remotehost = "192.168.240.253"
            remoteport = 61616
            connection = udp_conn.UDPConnection(localhost,localport,remotehost,remoteport)
            msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3,0, 0,7, 0,0,
                                  31, bytearray(0))
            connection.send_scp_message(msg)

    def test_send_scp_message_with_invalid_port_number(self):
        """
        The port number used when sending a packet over UDP has to be 7
        """
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            localhost = "127.0.0.1"
            localport = 54321
            remotehost = "127.0.0.1"
            remoteport = 61616
            connection = udp_conn.UDPConnection(localhost,localport,remotehost,remoteport)
            msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3,0, 0, 1, 0,0,
                                  0, bytearray(0))
            connection.send_scp_message(msg)

    def test_send_scp_message_with_invalid_cpu_number(self):
        """
        The cpu number used when sending a packet over UDP has to be 31
        """
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            localhost = "127.0.0.1"
            localport = 54321
            remotehost = "127.0.0.1"
            remoteport = 61616
            connection = udp_conn.UDPConnection(localhost,localport,remotehost,remoteport)
            msg = scp_msg.SCPMessage(flags.SDPFlag.REPLY_NOT_EXPECTED, 1, 0, 0, 0, cmds.SCPCommand.CMD_APLX, 1, 2, 3,0, 0, 7, 0,0,
                                  0, bytearray(0))
            connection.send_scp_message(msg)


if __name__ == '__main__':
    unittest.main()
