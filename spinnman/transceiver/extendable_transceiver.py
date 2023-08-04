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

# pylint: disable=too-many-arguments
from contextlib import contextmanager, suppress

from collections import defaultdict
import logging
import random
from threading import Condition, RLock
from spinn_utilities.abstract_base import (
    AbstractBase, abstractproperty, abstractmethod)
from spinn_utilities.log import FormatAdapter
from spinnman.transceiver.abstract_transceiver import AbstractTransceiver

logger = FormatAdapter(logging.getLogger(__name__))


class ExtendableTransceiver(AbstractTransceiver, metaclass=AbstractBase):
    """

    """
    __slots__ = [
        "_chip_execute_lock_condition",
        "_chip_execute_locks",
        "_flood_write_lock",
        "_n_chip_execute_locks",
        "_nearest_neighbour_id",
        "_nearest_neighbour_lock"
    ]

    def __init__(self):
        # A lock against single chip executions (entry is (x, y))
        # The condition should be acquired before the locks are
        # checked or updated
        # The write lock condition should also be acquired to avoid a flood
        # fill during an individual chip execute
        self._chip_execute_locks = defaultdict(Condition)
        self._chip_execute_lock_condition = Condition()
        self._n_chip_execute_locks = 0
        # A lock against multiple flood fill writes - needed as SCAMP cannot
        # cope with this
        self._flood_write_lock = Condition()

        # The nearest neighbour start ID and lock
        self._nearest_neighbour_id = 1
        self._nearest_neighbour_lock = RLock()

    @abstractproperty
    def bmp_connection(self):
        """
        Returns the BMP connection if there is one
        :rtype: BMPConnection or None
        """

    @abstractproperty
    def bmp_selector(self):
        """
        Returns the bmp selector

        :rtype: AbstractMultiConnectionProcessConnectionSelector
        """

    @abstractproperty
    def scamp_connection_selector(self):
        """
        Returns the scamp selector

        :rtype: AbstractMultiConnectionProcessConnectionSelector
        """

    @abstractmethod
    def where_is_xy(self, x, y):
        """
        Attempts to get where_is_x_y info from the machine

        If no machine will do its best.

        :param int x:
        :param int y:
        :rtype: str
        """

    @contextmanager
    def _flood_execute_lock(self):
        """
        Get a lock for executing a flood fill of an executable.
        """
        # Get the execute lock all together, so nothing can access it
        with self._chip_execute_lock_condition:
            # Wait until nothing is executing
            self._chip_execute_lock_condition.wait_for(
                lambda: self._n_chip_execute_locks < 1)
            yield self._chip_execute_lock_condition

    @staticmethod
    def _get_random_connection(connections):
        """
        Returns the given connection, or else picks one at random.

        :param list(Connection) connections:
            the list of connections to locate a random one from
        :return: a connection object
        :rtype: Connection or None
        """
        if not connections:
            return None
        return connections[random.randint(0, len(connections) - 1)]
