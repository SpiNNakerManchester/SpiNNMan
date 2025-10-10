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


from spinnman.spalloc import SpallocClient
import spinnman.spinnman_script as sim


SPALLOC_URL = "https://spinnaker.cs.man.ac.uk/spalloc"
# If None these are read from environment variables
SPALLOC_USERNAME = None
SPALLOC_PASSWORD = None

SPALLOC_MACHINE = "SpiNNaker1M"

# Scripts that the spinnman level use .spinnman.cfg
sim.setup(n_boards_required=1)

client = SpallocClient(SPALLOC_URL, SPALLOC_USERNAME, SPALLOC_PASSWORD)
job = client.create_job()
print(job)
# print("Waiting until ready...")
with job:
    job.wait_until_ready()
    print(job.get_connections())

    txrx = job.create_transceiver()
    # This call is for testing and can be changed without notice!
    dims = txrx._get_machine_dimensions()
    print(f"{dims.height=}, {dims.width=}")

    machine = txrx.get_machine_details()
    print(machine)

    # input("Press Enter to release...")
client.close()#print(2)#print(2^(1/(2^1)))
sim.end()