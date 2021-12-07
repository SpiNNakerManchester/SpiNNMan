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

from spinn_machine.data import MachineDataView
from spinn_machine.data.machine_data_writer import MachineDataWriter


class _SpiNNManDataModel(object):
    """
    Singleton data model

    This class should not be accessed directly please use the DataView and
    DataWriter classes.
    Accessing or editing the data held here directly is NOT SUPPORTED

    There may be other DataModel classes which sit next to this one and hold
    additional data. The DataView and DataWriter classes will combine these
    as needed.

    What data is held where and how can change without notice.
    """

    __singleton = None

    __slots__ = [
        # Data values cached
        "_transceiver",
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._clear()
        return obj

    def _clear(self):
        """
        Clears out all data
        """
        self._hard_reset()

    def _hard_reset(self):
        """
        Clears out all data that should change after a reset and graaph change
        """
        self._transceiver = None
        self._soft_reset()

    def _soft_reset(self):
        """
        Clears timing and other data that should changed every reset
        """
        # Holder for any later additions


class SpiNNManDataView(MachineDataView):
    """
    A read only view of the data available at Pacman level

    The objects accessed this way should not be changed or added to.
    Changing or adding to any object accessed if unsupported as bypasses any
    check or updates done in the writer(s).
    Objects returned could be changed to immutable versions without notice!

    The get methods will return either the value if known or a None.
    This is the faster way to access the data but lacks the safety.

    The property methods will either return a valid value or
    raise an Exception if the data is currently not available.
    These are typically semantic sugar around the get methods.

    The has methods will return True is the value is known and False if not.
    Semantically the are the same as checking if the get returns a None.
    They may be faster if the object needs to be generated on the fly or
    protected to be made immutable.

    While how and where the underpinning DataModel(s) store data can change
    without notice, methods in this class can be considered a supported API
    """

    __data = _SpiNNManDataModel()
    __slots__ = []

    # transceiver methods

    def has_transceiver(self):
        """
        Reports if a transceiver is currently set

        :rtype: bool
        """
        return self.__data._transceiver is not None

    @property
    def transceiver(self):
        """
        The transceiver description

        :rtype: ~spinnman.transceiver.Transceiver
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the machine is currently unavailable
        """
        if self.__data._transceiver is None:
             raise self._exception("transceiver")
        return self.__data._transceiver

    #def machine(self):
    #    if self.has_machine():
    #        return MachineDataView.machine
    #    machine = self.transceiver.read_machine()
    #    MachineDataWriter().set_machine(machine)
    #    return machine
