# Copyright (c) 2021 The University of Manchester
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
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinn_machine.data.machine_data_writer import MachineDataWriter
from spinnman.transceiver import Transceiver
from .spinnman_data_view import _SpiNNManDataModel, SpiNNManDataView

logger = FormatAdapter(logging.getLogger(__name__))
__temp_dir = None

REPORTS_DIRNAME = "reports"
# pylint: disable=protected-access


class SpiNNManDataWriter(MachineDataWriter, SpiNNManDataView):
    """
    See :py:class:`~spinn_utilities.data.UtilsDataWriter`

    This class is designed to only be used directly within the SpiNNMan
    repository unit tests as all methods are available to subclasses
    """
    __data = _SpiNNManDataModel()
    __slots__ = []

    def _spinnman_mock(self):
        """
        Like :py:meth:`_mock` but does not call superclass `_mock`.
        This method should only be called by `mock` via `_mock`
        """
        self.__data._clear()

    @overrides(MachineDataWriter._mock)
    def _mock(self):
        MachineDataWriter._mock(self)
        self._spinnman_mock()

    def _spinnman_setup(self):
        """
        Like :py:meth:`_setup` but does not call superclass `_setup`.

        This method should only be called by `setup` (via `_setup`)
        """
        self.__data._clear()

    @overrides(MachineDataWriter._setup)
    def _setup(self):
        MachineDataWriter._setup(self)
        self._spinnman_setup()

    def _local_hard_reset(self):
        """
        Puts spinnman data back into the state expected at graph changed and
        `sim.reset`.

        Unlike hard_reset this method does not call super classes

        This method should only be called by hard_reset (via _hard_reset)
        """

        self.__data._hard_reset()

    @overrides(MachineDataWriter._hard_reset)
    def _hard_reset(self):
        MachineDataWriter._hard_reset(self)
        self._local_hard_reset()

    def _local_soft_reset(self):
        """
        Puts all data back into the state expected at `sim.reset` but not
        graph changed.

        Unlike soft_reset this method does not call superclasses

        This method should only be called by soft_reset (via _soft_reset)
        """
        self.__data._soft_reset()

    @overrides(MachineDataWriter._soft_reset)
    def _soft_reset(self):
        MachineDataWriter._soft_reset(self)
        self._local_soft_reset()

    def set_transceiver(self, transceiver):
        """
        Sets the transceiver object.

        :param Transceiver transceiver:
        :raises TypeError: If the transceiver is not a Transceiver
        """
        if not isinstance(transceiver, Transceiver):
            raise TypeError("transceiver should be a Transceiver")
        if self.__data._transceiver:
            raise NotImplementedError(
                "Over writing and existing transceiver not supported")
        self.__data._transceiver = transceiver
