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

from typing import Iterable, Optional
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Connection
from spinnman.data import SpiNNManDataView
from spinnman.transceiver.base_transceiver import BaseTransceiver


class Version3Transceiver(BaseTransceiver):
    """
    Implementation of the Transceiver classes for Version 3 boards

    This class should ONLY be created via by transceiver_factory.py
    """

    @overrides(BaseTransceiver.__init__)
    def __init__(self, connections: Optional[Iterable[Connection]] = None,
                 power_cycle: bool = False,
                 ensure_board_is_ready: bool = True):
        """
        :param connections:
            An iterable of connections to the board.  If not specified, no
            communication will be possible until connections are found.
        :param power_cycle: If True will power cycle the machine:
        :param ensure_board_is_ready:
            Flag to say if ensure_board_is_ready should be run
        """
        super().__init__(connections, power_cycle, ensure_board_is_ready)
        assert SpiNNManDataView.get_machine_version().number == 3

    @property
    @overrides(BaseTransceiver.boot_led_0_value)
    def boot_led_0_value(self) -> int:
        return 0x00000502
