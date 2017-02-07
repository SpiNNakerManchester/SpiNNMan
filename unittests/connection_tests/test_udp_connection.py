import unittest
from board_test_configuration import BoardTestConfiguration
from spinnman.connections.udp_packet_connections.udp_scamp_connection \
    import UDPSCAMPConnection
import spinnman.exceptions as exc
from spinnman.messages.scp.impl import scp_read_link_request,\
    scp_read_memory_request, scp_version_request, scp_version_response
from spinnman.messages.scp.scp_result import SCPResult


board_config = BoardTestConfiguration()


class TestUDPConnection(unittest.TestCase):

    def test_scp_version_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = UDPSCAMPConnection(
            remote_host=board_config.remotehost)
        scp_req = scp_version_request.SCPVersionRequest(0, 0, 0)
        scp_response = scp_version_response.SCPVersionResponse()
        connection.send_scp_request(scp_req)
        _, _, data, offset = connection.receive_scp_response()
        scp_response.read_bytestring(data, offset)
        print scp_response.version_info
        self.assertEqual(
            scp_response._scp_response_header._result, SCPResult.RC_OK)

    def test_scp_read_link_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = UDPSCAMPConnection(
            remote_host=board_config.remotehost)
        scp_link = scp_read_link_request.SCPReadLinkRequest(
            0, 0, 0, 0x70000000, 250)
        connection.send_scp_request(scp_link)
        result, _, _, _ = connection.receive_scp_response()
        self.assertEqual(result, SCPResult.RC_OK)

    def test_scp_read_memory_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = UDPSCAMPConnection(
            remote_host=board_config.remotehost)
        scp_link = scp_read_memory_request.SCPReadMemoryRequest(
            0, 0, 0x70000000, 256)
        connection.send_scp_request(scp_link)
        result, _, _, _ = connection.receive_scp_response()
        self.assertEqual(result, SCPResult.RC_OK)

    def test_send_scp_request_to_nonexistent_host(self):
        with self.assertRaises(exc.SpinnmanTimeoutException):
            board_config.set_up_nonexistent_board()
            connection = UDPSCAMPConnection(
                remote_host=board_config.remotehost)
            scp = scp_read_memory_request.SCPReadMemoryRequest(0, 0, 0, 256)
            connection.send_scp_request(scp)
            _, _, _, _ = connection.receive_scp_response(2)

if __name__ == '__main__':
    unittest.main()
