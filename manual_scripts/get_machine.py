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

from requests.exceptions import ReadTimeout
from spinn_utilities.exceptions import DataNotYetAvialable
from spinnman.data import SpiNNManDataView
# Scripts that the spinnman level use .spinnman.cfg
import spinnman.spinnman_script as sim

sim.setup(n_boards_required=400)
# sim.setup()

machine1 = sim.get_machine()
print(machine1)
sim.end()