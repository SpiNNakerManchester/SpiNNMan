# Copyright (c) 2014 The University of Manchester
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

import logging
from typing import Optional
from threading import Condition, RLock
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod)
from spinn_utilities.log import FormatAdapter
from spinnman.connections.udp_packet_connections import BMPConnection
from spinnman.processes import ConnectionSelector, FixedConnectionSelector
from spinnman.transceiver.transceiver import Transceiver

logger = FormatAdapter(logging.getLogger(__name__))


class ExtendableTransceiver(Transceiver, metaclass=AbstractBase):
    """
    Support Functions to allow a Transceiver to also be an ExtendedTransceiver

    If supporting these is too difficult the
    methods that require these may be removed.
    """
    __slots__ = [
        "_flood_write_lock",
        "_nearest_neighbour_id",
        "_nearest_neighbour_lock"
    ]

    def __init__(self) -> None:

        # A lock against multiple flood fill writes - needed as SCAMP cannot
        # cope with this
        self._flood_write_lock = Condition()

        # The nearest neighbour start ID and lock
        self._nearest_neighbour_id = 1
        self._nearest_neighbour_lock = RLock()

    @property
    @abstractmethod
    def bmp_selector(self) -> Optional[FixedConnectionSelector[BMPConnection]]:
        """
        Returns the BMP selector
        """
        raise NotImplementedError("This method is abstract")

    @property
    @abstractmethod
    def scamp_connection_selector(self) -> ConnectionSelector:
        """
        Returns the scamp selector
        """
        raise NotImplementedError("This method is abstract")
