# Copyright (c) 2023 The University of Manchester
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

from typing import List, Optional
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Connection
from spinnman.data import SpiNNManDataView
from spinnman.transceiver.base_transceiver import BaseTransceiver


class Version5Transceiver(BaseTransceiver):
    """
    Implementation of the Transceiver classes for Version 5 boards

    This class should ONLY be created via by transceiver_factory.py
    """

    @overrides(BaseTransceiver.__init__)
    def __init__(self, connections: Optional[List[Connection]] = None,
                 power_cycle: bool = False):
        super().__init__(connections, power_cycle)
        assert SpiNNManDataView.get_machine_version().number == 5

    @property
    @overrides(BaseTransceiver.boot_led_0_value)
    def boot_led_0_value(self) -> int:
        return 0x00000001
