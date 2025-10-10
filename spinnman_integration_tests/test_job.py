# Copyright (c) 2024 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from requests.exceptions import ConnectionError
from spinn_utilities.config_holder import set_config

from spinn_machine.version import FIVE

from spinnman.config_setup import unittest_setup
from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.spalloc import SpallocClient, SpallocState


class TestTransceiver(unittest.TestCase):

    def test_create_job(self) -> None:
        unittest_setup()
        set_config("Machine", "version", str(FIVE))
        self.spalloc_url = "https://spinnaker.cs.man.ac.uk/spalloc"
        self.spalloc_machine = "SpiNNaker1M"
        writer = SpiNNManDataWriter.mock()
        writer.set_n_required(n_boards_required=2, n_chips_required=None)

        try:
            client = SpallocClient(self.spalloc_url)
        except ConnectionError as ex:
            raise unittest.SkipTest(str(ex))
        job = client.create_job()
        with job:
            job.wait_until_ready()

            connections = job.get_connections()
            self.assertGreaterEqual(len(connections), 2)
            self.assertIn((0, 0), connections)

            txrx = job.create_transceiver(ensure_board_is_ready=True)

            dims = txrx._get_machine_dimensions()  # type: ignore[attr-defined]
            # May be 12 as we only asked for 2 boards
            self.assertGreaterEqual(dims.height, 12)
            self.assertGreaterEqual(dims.width, 12)

            machine = txrx.get_machine_details()
            self.assertGreaterEqual(len(machine.ethernet_connected_chips), 2)

            state = job.get_state()
            self.assertEqual(state, SpallocState.READY)

            credentials = job.get_session_credentials_for_db()
            self.assertIn(('SPALLOC', 'service uri'), credentials)
            self.assertIn(('SPALLOC', 'job uri'), credentials)
            self.assertIn(('COOKIE', 'JSESSIONID'), credentials)
            self.assertIn(('HEADER', 'X-CSRF-TOKEN'), credentials)

        client.close()  # print(2^(1/(2^1)


if __name__ == '__main__':
    unittest.main()
