__author__ = 'Petrut'

import unittest
import spinnman.connections.udp_connection as udp_conn
import spinnman.messages.scp.scp_request_header as scp_msg
import spinnman.exceptions as exc
import spinnman.messages.sdp.sdp_header as sdp_header
import spinnman.messages.sdp.sdp_flag as flags
import spinnman.messages.scp.scp_command as cmds
from spinnman.messages.scp.impl import scp_read_link_request,scp_read_link_response,scp_read_memory_request,scp_read_memory_response\
                ,scp_version_request, scp_version_response
from spinnman.messages.scp.scp_result import SCPResult
import time
import thread

class TestUDPConnection(unittest.TestCase):

    def set_up_local_virtual_board(self):
        self.localhost = "127.0.0.1"
        self.localport = 54321
        self.remotehost = "127.0.0.1"
        self.remoteport = 17893

    def set_up_remote_board(self):
        self.localhost = "192.168.240.254"
        self.localport = 54321
        self.remotehost = "192.168.240.253"
        self.remoteport = 17893

    def test_setup_new_local_udp_connection(self):
        self.set_up_local_virtual_board()
        connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
        self.assertEqual(connection.local_ip_address, self.localhost)
        self.assertEqual(connection.local_port, self.localport)

    def test_setup_new_remote_udp_connection(self):
        self.set_up_remote_board()
        connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
        self.assertEqual(connection.local_ip_address, self.localhost)
        self.assertEqual(connection.local_port, self.localport)

    def test_scp_version_request_and_response_board(self):
        self.set_up_remote_board()
        connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
        scp_req = scp_version_request.SCPVersionRequest(0,0,0)
        scp_response = scp_version_response.SCPVersionResponse()
        connection.send_scp_request(scp_req)
        connection.receive_scp_response(scp_response)
        print scp_response.version_info
        self.assertEqual(scp_response._scp_response_header._result, SCPResult.RC_OK)


    def test_scp_version_request_and_response_board_invalid_x(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            self.set_up_remote_board()
            connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
            scp_req = scp_version_request.SCPVersionRequest(256,0,0)


    def test_scp_version_request_and_response_board_invalid_y(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            self.set_up_remote_board()
            connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
            scp_req = scp_version_request.SCPVersionRequest(0,256,0)


    def test_scp_version_request_and_response_board_invalid_processor(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            self.set_up_remote_board()
            connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
            scp_req = scp_version_request.SCPVersionRequest(0,0,32)


    def test_scp_read_link_request_and_response_board(self):
        self.set_up_remote_board()
        connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
        scp_link = scp_read_link_request.SCPReadLinkRequest(0,0,0,0,250)
        scp_link_reader = scp_read_link_response.SCPReadLinkResponse()
        connection.send_scp_request(scp_link)
        connection.receive_scp_response(scp_link_reader)
        self.assertEqual(scp_link_reader._scp_response_header._result, SCPResult.RC_OK)

    def test_scp_read_memory_request_and_response_board(self):
        self.set_up_remote_board()
        connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
        scp_link = scp_read_memory_request.SCPReadMemoryRequest(0,0,0,256)
        scp_link_reader = scp_read_memory_response.SCPReadMemoryResponse()
        connection.send_scp_request(scp_link)
        connection.receive_scp_response(scp_link_reader)
        self.assertEqual(scp_link_reader._scp_response_header._result, SCPResult.RC_OK)


    def test_scp_read_memory_request_and_response_board_more_than_256_bytes(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            self.set_up_remote_board()
            connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
            scp_link = scp_read_memory_request.SCPReadMemoryRequest(0,0,0,257)

    def test_scp_read_memory_request_and_response_board_0_bytes(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            self.set_up_remote_board()
            connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
            scp_link = scp_read_memory_request.SCPReadMemoryRequest(0,0,0,0)

    def test_send_scp_request_to_nonexistent_host(self):
        with self.assertRaises(exc.SpinnmanTimeoutException):
            localhost = "192.168.240.254"
            localport = 54321
            remotehost = "192.168.240.253"
            remoteport = 11111
            connection = udp_conn.UDPConnection(localhost,localport,remotehost,remoteport)
            scp = scp_read_memory_request.SCPReadMemoryRequest(0,0,0,256)
            scp_reader = scp_read_memory_response.SCPReadMemoryResponse()
            connection.send_scp_request(scp)
            connection.receive_scp_response(scp_reader,2)

    # def test_send_boot_message(self):
    #     self.set_up_remote_board()
    #     connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)

    # def test_scp_read_link_request_and_response_virtual_board(self):
    #     self.set_up_local_virtual_board()
    #     connection = udp_conn.UDPConnection(self.localhost,self.localport,self.remotehost,self.remoteport)
    #     scp_link = scp_read_link_request.SCPReadLinkRequest(0,0,0,0,250)
    #     scp_link_reader = scp_read_memory_response.SCPReadMemoryResponse()
    #     connection.send_scp_request(scp_link)
    #     print connection.receive_scp_response(scp_link_reader)

if __name__ == '__main__':
    unittest.main()
