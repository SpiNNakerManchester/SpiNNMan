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
from spinnman.utilities.appid_tracker import AppIdTracker


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
        "_app_id_tracker",
        "_scamp_connection_selector",
        "_transceiver",
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
        # pylint: disable=protected-access
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._transceiver = None
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
        self._app_id_tracker = None
        self._clear_transceiver()
        self._soft_reset()

    def _clear_transceiver(self):
        self._scamp_connection_selector = None
        if self._transceiver:
            try:
                self._transceiver.close()
            except Exception:
                pass
        self._transceiver = None

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

    def get_transceiver(self):
        """
        The transceiver description or None if the is no tranceiver

        :rtype: ~spinnman.transceiver.Transceiver
        """
        return self.__data._transceiver

    def read_memory(self, x, y, base_address, length, cpu=0):
        """ Read some areas of memory (usually SDRAM) from the board.

        Semantic sugar for transceiver.read_memory

        :param int x:
            The x-coordinate of the chip where the memory is to be read from
        :param int y:
            The y-coordinate of the chip where the memory is to be read from
        :param int base_address:
            The address in SDRAM where the region of memory to be read starts
        :param int length: The length of the data to be read in bytes
        :param int cpu:
            the core ID used to read the memory of; should usually be 0 when
            reading from SDRAM, but may be other values when reading from DTCM.
        :return: A bytearray of data read
        :rtype: bytes
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of `x`, `y`, `cpu`, `base_address` or `length` is invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if self.__data._transceiver is None:
            raise self._exception("transceiver")
        return self.__data._transceiver.read_memory(
            x, y, base_address, length, cpu)

    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False):
        """ Write to the SDRAM on the board.

        Semantic sugar for transceiver.read_memory

        :param int x:
            The x-coordinate of the chip where the memory is to be written to
        :param int y:
            The y-coordinate of the chip where the memory is to be written to
        :param int base_address:
            The address in SDRAM where the region of memory is to be written
        :param data: The data to write.  Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A single integer - will be written in little-endian byte order
            * A filename of a data file (in which case `is_filename` must be\
              set to True)
        :type data:
            ~io.RawIOBase or bytes or bytearray or int or str
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be\
              used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the length of the file will be used
        :param int offset: The offset from which the valid data begins
        :param int cpu: The optional CPU to write to
        :param bool is_filename: True if `data` is a filename
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the data
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If `x, y` does not lead to a valid chip
            * If a packet is received that has invalid parameters
            * If `base_address` is not a positive integer
            * If `data` is an RawIOBase but `n_bytes` is not specified
            * If `data` is an int and `n_bytes` is more than 4
            * If `n_bytes` is less than 0
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if self.__data._transceiver is None:
            raise self._exception("transceiver")
        return self.__data._transceiver.write_memory(
            x, y, base_address, data, n_bytes, offset, cpu, is_filename)

    @property
    def app_id_tracker(self):
        if self.__data._app_id_tracker is None:
            self.__data._app_id_tracker = AppIdTracker()
        return self.__data._app_id_tracker

    def get_new_id(self):
        """
        Gets a new id from the current app_id_tracker

        currently semantic sugar for transceiver.app_id_tracker.get_new_id()

        :rtype: AppIdTracker
        """
        return self.app_id_tracker.get_new_id()

    @property
    def scamp_connection_selector(self):
        """
        Gets the scamp connection selector from the transceiver

        Semantic sugar for transceiver.scamp_connection_selector

        :rtype: MostDirectConnectionSelector
        """
        if not self.__data._scamp_connection_selector:
            if self.__data._transceiver is None:
                raise self._exception("transceiver")
            self.__data._scamp_connection_selector =\
                self.__data._transceiver._scamp_connection_selector
        return self.__data._scamp_connection_selector

    # def machine(self):
    #    if self.has_machine():
    #        return MachineDataView.machine
    #    machine = self.transceiver.read_machine()
    #    MachineDataWriter().set_machine(machine)
    #    return machine
