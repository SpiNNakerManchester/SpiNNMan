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

from requests.exceptions import ConnectionError
import unittest
from spinn_utilities.config_holder import set_config

from spinn_machine.version import FIVE
from spinnman.config_setup import unittest_setup
from spinnman.spalloc import SpallocClient, SpallocState


class TestTransceiver(unittest.TestCase):

    def setUp(self):
        unittest_setup()
        set_config("Machine", "version", FIVE)
        self.spalloc_url = "https://spinnaker.cs.man.ac.uk/spalloc"
        self.spalloc_machine = "SpiNNaker1M"

    def test_create_job(self):
        try:
            client = SpallocClient(self.spalloc_url)
        except ConnectionError as ex:
            raise unittest.SkipTest(str(ex))
        except Exception as ex:
            raise NotImplementedError(str(type(ex)))
        # job = client.create_job_rect_at_board(
        #    WIDTH, HEIGHT, triad=(x, y, b), machine_name=SPALLOC_MACHINE,
        #    max_dead_boards=1)
        job = client.create_job(
            num_boards=2, machine_name=self.spalloc_machine)
        with job:
            job.wait_until_ready()

            connections = job.get_connections()
            self.assertGreaterEqual(len(connections), 2)
            self.assertIn((0, 0), connections)

            txrx = job.create_transceiver()

            dims = txrx._get_machine_dimensions()
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
        pop = 1/0

if __name__ == '__main__':
    unittest.main()
