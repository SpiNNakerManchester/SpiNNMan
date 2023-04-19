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
from spinn_machine.data import MachineDataView
from spinnman.utilities.appid_tracker import AppIdTracker

logger = FormatAdapter(logging.getLogger(__name__))
# pylint: disable=protected-access


class _SpiNNManDataModel(object):
    """
    Singleton data model.

    This class should not be accessed directly please use the DataView and
    DataWriter classes.
    Accessing or editing the data held here directly is *not supported!*

    There may be other DataModel classes which sit next to this one and hold
    additional data. The DataView and DataWriter classes will combine these
    as needed.

    What data is held where and how can change without notice.
    """

    __singleton = None

    __slots__ = [
        # Data values cached
        "_app_id",
        "_app_id_tracker",
        "_scamp_connection_selector",
        "_transceiver",
    ]

    def __new__(cls):
        if cls.__singleton:
            return cls.__singleton
        obj = object.__new__(cls)
        cls.__singleton = obj
        obj._transceiver = None
        obj._clear()
        return obj

    def _clear(self):
        """
        Clears out all data.
        """
        self._hard_reset()

    def _hard_reset(self):
        """
        Clears out all data that should change after a reset and graph change.
        """
        self._app_id = None
        self._app_id_tracker = None
        self._soft_reset()
        self._scamp_connection_selector = None
        if self._transceiver:
            try:
                self._transceiver.close()
            except Exception as ex:  # pylint: disable=broad-except
                logger.exception(
                    f"Error {ex} when closing the transceiver ignored")
        self._transceiver = None

    def _soft_reset(self):
        """
        Clears timing and other data that should changed every reset.
        """
        # Holder for any later additions


class SpiNNManDataView(MachineDataView):
    """
    Adds the extra Methods to the View for SpiNNMan level.

    See :py:class:`~spinn_utilities.data.UtilsDataView` for a more detailed
    description.

    This class is designed to only be used directly within the SpiNNMan
    repository as all methods are available to subclasses
    """

    __data = _SpiNNManDataModel()
    __slots__ = []

    # transceiver methods

    @classmethod
    def has_transceiver(cls):
        """
        Reports if a transceiver is currently set.

        :rtype: bool
        """
        return cls.__data._transceiver is not None

    @classmethod
    def get_transceiver(cls):
        """
        The transceiver description.

        :rtype: ~spinnman.transceiver.Transceiver
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver

    @classmethod
    def read_memory(cls, x, y, base_address, length, cpu=0):
        """
        Read some areas of memory (usually SDRAM) from the board.

        Syntactic sugar for `get_transceiver().read_memory()`.

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
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
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
        try:
            return cls.__data._transceiver.read_memory(
                x, y, base_address, length, cpu)
        except AttributeError as ex:
            raise cls._exception("transceiver") from ex

    @classmethod
    def write_memory(cls, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False):
        """
        Write to the SDRAM on the board.

        Syntactic sugar for `get_transceiver().write_memory()`.

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
            * If `data` is a byte string (bytearray or bytes), the length of\
              the byte string will be used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the length of the file will be used
        :param int offset: The offset from which the valid data begins
        :param int cpu: The optional CPU to write to
        :param bool is_filename: True if `data` is a filename
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
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
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.write_memory(
            x, y, base_address, data, n_bytes, offset, cpu, is_filename)

    # app_id methods

    @classmethod
    def get_app_id(cls):
        """
        Gets the main app_id used by the transceiver.

        This method will create a new app_id if one has not yet been created.

        :rtype: int
        """
        if cls.__data._app_id is None:
            cls.__data._app_id = cls.get_new_id()
        return cls.__data._app_id

    @classmethod
    def get_new_id(cls):
        """
        Gets a new id from the current `app_id_tracker`

        previously `get_transceiver().app_id_tracker().get_new_id()`

        :rtype: AppIdTracker
        """
        if cls.__data._app_id_tracker is None:
            cls.__data._app_id_tracker = AppIdTracker()
        return cls.__data._app_id_tracker.get_new_id()

    @classmethod
    def free_id(cls, app_id):
        """
        Frees up an app_id.

        previously `get_transceiver().app_id_tracker().free_id(app_id)`

        :param int app_id:
        """
        if cls.__data._app_id_tracker:
            cls.__data._app_id_tracker.free_id(app_id)

    @classmethod
    def get_scamp_connection_selector(cls):
        """
        Gets the SCAMP connection selector from the transceiver.

        Syntactic sugar for `get_transceiver().scamp_connection_selector()`

        :rtype: MostDirectConnectionSelector
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        """
        if not cls.__data._scamp_connection_selector:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver")
            cls.__data._scamp_connection_selector =\
                cls.__data._transceiver._scamp_connection_selector
        return cls.__data._scamp_connection_selector
