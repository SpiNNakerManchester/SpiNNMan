import unittest
from spinnman.board_test_configuration import BoardTestConfiguration
from spinnman.connections.udp_packet_connections.udp_spinnaker_connection \
    import UDPSpinnakerConnection
import spinnman.exceptions as exc
from spinnman.messages.scp.impl import scp_read_link_request,\
    scp_read_link_response, scp_read_memory_request, scp_read_memory_response,\
    scp_version_request, scp_version_response
from spinnman.messages.scp.scp_result import SCPResult


board_config = BoardTestConfiguration()


class TestUDPConnection(unittest.TestCase):

    def test_setup_new_local_udp_connection(self):
        board_config.set_up_local_virtual_board()
        connection = UDPSpinnakerConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost)
        self.assertEqual(connection.local_ip_address, board_config.localhost)
        self.assertEqual(connection.local_port, board_config.localport)

    def test_setup_new_remote_udp_connection(self):
        board_config.set_up_remote_board()
        connection = UDPSpinnakerConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost)
        print connection
        self.assertEqual(connection.local_ip_address, board_config.localhost)
        self.assertEqual(connection.local_port, board_config.localport)

    def test_scp_version_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = UDPSpinnakerConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost)
        scp_req = scp_version_request.SCPVersionRequest(0, 0, 0)
        scp_response = scp_version_response.SCPVersionResponse()
        connection.send_scp_request(scp_req)
        connection.receive_scp_response(scp_response)
        print scp_response.version_info
        self.assertEqual(
            scp_response._scp_response_header._result, SCPResult.RC_OK)

    def test_scp_version_request_and_response_board_invalid_x(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            board_config.set_up_remote_board()
            connection = UDPSpinnakerConnection(
                board_config.localhost, board_config.localport,
                board_config.remotehost)
            scp_req = scp_version_request.SCPVersionRequest(256, 0, 0)

    def test_scp_version_request_and_response_board_invalid_y(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            board_config.set_up_remote_board()
            connection = UDPSpinnakerConnection(
                board_config.localhost, board_config.localport,
                board_config.remotehost)
            scp_req = scp_version_request.SCPVersionRequest(0, 256, 0)

    def test_scp_version_request_and_response_board_invalid_processor(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            board_config.set_up_remote_board()
            connection = UDPSpinnakerConnection(
                board_config.localhost, board_config.localport,
                board_config.remotehost)
            scp_req = scp_version_request.SCPVersionRequest(0, 0, 32)

    def test_scp_read_link_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = UDPSpinnakerConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost)
        scp_link = scp_read_link_request.SCPReadLinkRequest(0, 0, 0, 0, 0, 250)
        scp_link_reader = scp_read_link_response.SCPReadLinkResponse()
        connection.send_scp_request(scp_link)
        connection.receive_scp_response(scp_link_reader)
        self.assertEqual(
            scp_link_reader._scp_response_header._result, SCPResult.RC_OK)

    def test_scp_read_memory_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = UDPSpinnakerConnection(
            board_config.localhost, board_config.localport,
            board_config.remotehost)
        scp_link = scp_read_memory_request.SCPReadMemoryRequest(0, 0, 0, 256)
        scp_link_reader = scp_read_memory_response.SCPReadMemoryResponse()
        connection.send_scp_request(scp_link)
        connection.receive_scp_response(scp_link_reader)
        self.assertEqual(
            scp_link_reader._scp_response_header._result, SCPResult.RC_OK)

    def test_scp_read_memory_request_and_response_board_more_than_256_bytes(
            self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            board_config.set_up_remote_board()
            connection = UDPSpinnakerConnection(
                board_config.localhost, board_config.localport,
                board_config.remotehost)
            scp_link = scp_read_memory_request.SCPReadMemoryRequest(
                0, 0, 0, 257)

    def test_scp_read_memory_request_and_response_board_0_bytes(self):
        with self.assertRaises(exc.SpinnmanInvalidParameterException):
            board_config.set_up_remote_board()
            connection = UDPSpinnakerConnection(
                board_config.localhost, board_config.localport,
                board_config.remotehost)
            scp_link = scp_read_memory_request.SCPReadMemoryRequest(0, 0, 0, 0)

    def test_send_scp_request_to_nonexistent_host(self):
        with self.assertRaises(exc.SpinnmanTimeoutException):
            board_config.set_up_nonexistent_board()
            connection = UDPSpinnakerConnection(
                board_config.localhost, board_config.localport,
                board_config.remotehost)
            scp = scp_read_memory_request.SCPReadMemoryRequest(0, 0, 0, 256)
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
