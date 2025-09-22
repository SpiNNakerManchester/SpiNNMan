# Copyright (c) 2025 The University of Manchester
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

from spinn_utilities.exceptions import DataNotYetAvialable
from spinnman.data import SpiNNManDataView
# Scripts that the spinnman level use .spinnman.cfg
import spinnman.spinnman_script as sim

# sim.setup(n_boards_required=2)
sim.setup()

assert SpiNNManDataView.has_transceiver() == False
try:
    SpiNNManDataView.get_transceiver()
    raise AssertionError("SpiNNManDataView.get_transceiver() worked??")
except DataNotYetAvialable:
    pass

# get_transceiver method is purely for debugging
# Can be called with ensure_board_is_ready=True
transceiver1 = sim.get_transceiver(ensure_board_is_ready=False)
print(transceiver1, id(transceiver1))
assert SpiNNManDataView.has_transceiver() == True
transceiver2 = SpiNNManDataView.get_transceiver()
assert id(transceiver2) == id(transceiver1)

try:
    SpiNNManDataView.get_machine()
    raise AssertionError("SpiNNManDataView.get_machine() worked??")
except DataNotYetAvialable:
    pass

# get_machine will call get_transceiver(ensure_board_is_ready=True)
machine1 = sim.get_machine()
print(machine1)

machine2 = SpiNNManDataView.get_machine()
assert id(machine2) == id(machine1)

# get_transceiver will return the same transceiver every time
transceiver2 = sim.get_transceiver(ensure_board_is_ready=False)
assert id(transceiver2) == id(transceiver1)

sim.end()

# Like other scripts DataView still has (useless) Transceiver object
assert SpiNNManDataView.has_transceiver() == True
transceiver2 = SpiNNManDataView.get_transceiver()
assert id(transceiver2) == id(transceiver1)

# sim route fails
try:
    sim.get_transceiver()
    raise AssertionError("SpiNNManDataView.get_transceiver() worked??")
except AssertionError:
    pass

# Like other scripts DataView still has Machine object
machine2 = SpiNNManDataView.get_machine()
assert id(machine2) == id(machine1)

# sim route fails
try:
    sim.get_machine()
    raise AssertionError("SpiNNManDataView.get_machine() worked??")
except AssertionError:
    pass
