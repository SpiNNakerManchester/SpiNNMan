# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from spinn_utilities.log import FormatAdapter
from spinn_machine.data.machine_data_writer import MachineDataWriter
from spinnman.transceiver import Transceiver
from .spinnman_data_view import _SpiNNManDataModel, SpiNNManDataView

logger = FormatAdapter(logging.getLogger(__name__))
__temp_dir = None

REPORTS_DIRNAME = "reports"


class SpiNNManDataWriter(MachineDataWriter, SpiNNManDataView):
    """
    Writer class for the Fec Data

    """
    __data = _SpiNNManDataModel()
    __slots__ = []

    def mock(self):
        """
        Clears out all data and adds mock values where needed.

        This should set the most likely defaults values.
        But be aware that what is considered the most likely default could
        change over time.

        Unittests that depend on any valid value being set should be able to
        depend on Mock.

        Unittest that depend on a specific value should call mock and then
        set that value.
        """
        MachineDataWriter.mock(self)
        self.__data._clear()

    def setup(self):
        """
        Puts all data back into the state expected at sim.setup time

        """
        MachineDataWriter.setup(self)
        self.__data._clear()

    def hard_reset(self):
        MachineDataWriter.hard_reset(self)
        self.__data._hard_reset()

    def soft_reset(self):
        MachineDataWriter.soft_reset(self)
        self.__data._soft_reset()

    def set_transceiver(self, transceiver):
        if self.__data._transceiver:
            self.__data._transceiver.close()
        # Must do a delayed import here so Transceiver can call this
        if not isinstance(transceiver, Transceiver):
            raise TypeError("transceiver should be a Transceiver")
        self.__data._transceiver = transceiver

    def clear_transceiver(self):
        if self.__data._transceiver:
            self.__data._transceiver.close()
        self.__data._transceiver = None
        self.__data._scamp_connection_selector = None