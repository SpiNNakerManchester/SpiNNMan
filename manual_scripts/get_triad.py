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

from spinn_utilities.config_holder import set_config
from spinnman.spalloc import SpallocClient
from spinnman.config_setup import unittest_setup


SPALLOC_URL = "https://spinnaker.cs.man.ac.uk/spalloc"
SPALLOC_USERNAME = ""
SPALLOC_PASSWORD = ""

SPALLOC_MACHINE = "SpiNNaker1M"

x = 0
y = 3
b = 0 # Must be 0 if requesting a rect
RECT = True
WIDTH = 1  # In triads!
HEIGHT = 1 # In triads!

unittest_setup()
set_config("Machine", "version",5)
client = SpallocClient(SPALLOC_URL, SPALLOC_USERNAME, SPALLOC_PASSWORD)
if RECT:
    job = client.create_job_rect_at_board(
        WIDTH, HEIGHT, triad=(x, y, b), machine_name=SPALLOC_MACHINE,
        max_dead_boards=1)
else:
    job = client.create_job_board(
        triad=(x, y, b), machine_name=SPALLOC_MACHINE)
print(job)
print("Waiting until ready...")
with job:
    job.wait_until_ready()
    print(job.get_connections())

    txrx = job.create_transceiver()
    # This call is for testing and can be changed without notice!
    dims = txrx._get_machine_dimensions()
    print(f"{dims.height=}, {dims.width=}")

    machine = txrx.get_machine_details()
    print(machine)

    input("Press Enter to release...")
client.close()#print(2)#print(2^(1/(2^1)))