# Copyright (c) 2017-2023 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.config_setup import unittest_setup
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.scp.impl import GetVersion, ReadLink, ReadMemory
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.scp.impl.get_version_response import GetVersionResponse
from board_test_configuration import BoardTestConfiguration

board_config = BoardTestConfiguration()


class TestUDPConnection(unittest.TestCase):

    def setUp(self):
        unittest_setup()

    def test_scp_version_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = SCAMPConnection(
            remote_host=board_config.remotehost)
        scp_req = GetVersion(0, 0, 0)
        scp_response = GetVersionResponse()
        connection.send_scp_request(scp_req)
        _, _, data, offset = connection.receive_scp_response()
        scp_response.read_bytestring(data, offset)
        print(scp_response.version_info)
        self.assertEqual(
            scp_response._scp_response_header._result, SCPResult.RC_OK)

    def test_scp_read_link_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = SCAMPConnection(
            remote_host=board_config.remotehost)
        scp_link = ReadLink(0, 0, 0, 0x70000000, 250)
        connection.send_scp_request(scp_link)
        result, _, _, _ = connection.receive_scp_response()
        self.assertEqual(result, SCPResult.RC_OK)

    def test_scp_read_memory_request_and_response_board(self):
        board_config.set_up_remote_board()
        connection = SCAMPConnection(
            remote_host=board_config.remotehost)
        scp_link = ReadMemory(0, 0, 0x70000000, 256)
        connection.send_scp_request(scp_link)
        result, _, _, _ = connection.receive_scp_response()
        self.assertEqual(result, SCPResult.RC_OK)

    def test_send_scp_request_to_nonexistent_host(self):
        with self.assertRaises(SpinnmanTimeoutException):
            board_config.set_up_nonexistent_board()
            connection = SCAMPConnection(
                remote_host=board_config.remotehost)
            scp = ReadMemory(0, 0, 0, 256)
            connection.send_scp_request(scp)
            _, _, _, _ = connection.receive_scp_response(2)


if __name__ == '__main__':
    unittest.main()
