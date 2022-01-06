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
from spinn_utilities.overrides import overrides
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

    def _spinnman_mock(self):
        """
        Like _mock but does not call super class _mock
        """
        self.__data._clear()

    @overrides(MachineDataWriter._mock)
    def _mock(self):
        MachineDataWriter._mock(self)
        self._spinnman_mock()

    def _spinnman_setup(self):
        """
        Like _setup but does not call super class _setup
        """
        self.__data._clear()

    @overrides(MachineDataWriter._setup)
    def _setup(self):
        MachineDataWriter._setup(self)
        self._spinnman_setup()

    def local_hard_reset(self):
        self.__data._hard_reset()

    def hard_reset(self):
        MachineDataWriter.hard_reset(self)
        self.local_hard_reset()

    def local_soft_reset(self):
        self.__data._soft_reset()

    def soft_reset(self):
        MachineDataWriter.soft_reset(self)
        self.local_soft_reset()

    def set_transceiver(self, transceiver):
        if self.__data._transceiver:
            self.__data._transceiver.close()
        if not isinstance(transceiver, Transceiver):
            raise TypeError("transceiver should be a Transceiver")
        self.__data._transceiver = transceiver

    def clear_transceiver(self):
        self.__data._clear_transceiver()
