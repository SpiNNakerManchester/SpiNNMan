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
    def read_core_state_count(cls, app_id, state):
        """
        Get a count of the number of cores which have a given state.

        Syntactic sugar for `get_transceiver().get_core_state_count`.

        :param int app_id:
            The ID of the application from which to get the count.
        :param CPUState state: The state count to get
        :return: A count of the cores with the given status
        :rtype: int
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If state is not a valid status
            * If app_id is not a valid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.get_core_state_count(app_id, state)
        except AttributeError as ex:
            raise cls._exception("transceiver") from ex

    @classmethod
    def read_cpu_information_from_core(cls, x, y, p):
        """
        Get information about a specific processor on the board.

        Syntactic sugar for
        `get_transceiver().get_cpu_information_from_core()`.

        :param int x: The x-coordinate of the chip containing the processor
        :param int y: The y-coordinate of the chip containing the processor
        :param int p: The ID of the processor to get the information about
        :return: The CPU information for the selected core
        :rtype: CPUInfo
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y, p is not a valid processor
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.get_cpu_information_from_core(
                x, y, p)
        except AttributeError as ex:
            raise cls._exception("transceiver") from ex

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
    def read_word(cls, x, y, base_address, cpu=0):
        """
        Read a word (usually of SDRAM) from the board.

        Syntactic sugar for `get_transceiver().read_word()`.

        :param int x:
            The x-coordinate of the chip where the word is to be read from
        :param int y:
            The y-coordinate of the chip where the word is to be read from
        :param int base_address:
            The address (usually in SDRAM) where the word to be read starts
        :param int cpu:
            the core ID used to read the word; should usually be 0 when reading
            from SDRAM, but may be other values when reading from DTCM.
        :return: The unsigned integer value at ``base_address``
        :rtype: int
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of `x`, `y`, `cpu` or `base_address` is invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.read_word(
                x, y, base_address, cpu)
        except AttributeError as ex:
            raise cls._exception("transceiver") from ex

    @classmethod
    def read_cores_in_state(cls, all_core_subsets, states):
        """
        Get all cores that are in a given state or set of states.

        Syntactic sugar for `get_transceiver().get_cores_in_state`.

        :param ~spinn_machine.CoreSubsets all_core_subsets:
            The cores to filter
        :param states: The state or states to filter on
        :type states: CPUState or set(CPUState)
        :return: Core subsets object containing cores in the given state(s)
        :rtype: CPUInfos
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        """
        try:
            return cls.__data._transceiver.get_cores_in_state(
                all_core_subsets, states)
        except AttributeError as ex:
            raise cls._exception("transceiver") from ex

    @classmethod
    def read_user(cls, user, x, y, p):
        """
        Get the contents of this user register for the given processor.

        Syntactic sugar for `get_transceiver().read_user`.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param int user: The user number to get the address for
        :param int x: X coordinate of the chip
        :param int y: Y coordinate of the chip
        :param int p: Virtual processor identifier on the chip
        :rtype: int
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.read_user(user, x, y, p)
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

    @classmethod
    def write_signal(cls, app_id, signal):
        """
        Writes/ Sends a signal to an application.

        Syntactic sugar for `get_transceiver().send_signal`.

        :param int app_id: The ID of the application to send to
        :param Signal signal: The signal to send
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If signal is not a valid signal
            * If app_id is not a valid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.send_signal(app_id, signal)

    @classmethod
    def write_stop_application(cls, app_id):
        """
        Sends a stop request for an app_id.

        Syntactic sugar for `get_transceiver().stop_application`.

        :param int app_id: The ID of the application to send to
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If app_id is not a valid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.stop_application(app_id)

    @classmethod
    def write_update_provenance_and_exit(cls, x, y, p):
        """
        Sends a command to update prevenance and exit

        Syntactic sugar for `get_transceiver().update_provenance_and_exit`.

        :param int x:
            The x-coordinate of the core
        :param int y:
            The y-coordinate of the core
        :param int p:
            The processor on the core
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.update_provenance_and_exit(x, y, p)

    @classmethod
    def write_user(cls, user, x, y, p, value):
        """
        Write to this user register for the given processor.

        Syntactic sugar for `get_transceiver().write_user`.

        .. note::
            Conventionally, user_0 usually holds the address of the table of
            memory regions.

        :param int user: The user to write to
        :param int x: X coordinate of the chip
        :param int y: Y coordinate of the chip
        :param int p: Virtual processor identifier on the chip
        :param int value: The value to write
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.write_user(user, x, y, p, value)

    @classmethod
    def wait_for_cores_to_be_in_state(
            cls, all_core_subsets, app_id, cpu_states, timeout,
            error_states=None, progress_bar=None):
        """
        Waits for the specified cores running the given application to be
        in some target state or states. Handles failures.

        Syntactic sugar for `get_transceiver().wait_for_cores_to_be_in_state`.

        :param ~spinn_machine.CoreSubsets all_core_subsets:
            the cores to check are in a given sync state
        :param int app_id: the application ID that being used by the simulation
        :param set(CPUState) cpu_states:
            The expected states once the applications are ready; success is
            when each application is in one of these states
        :param timeout:
            The amount of time to wait in seconds for the cores to reach one
            of the states.
        :tpye timeout: float or None
        :param set(CPUState) error_states:
            Set of states that the application can be in that indicate an
            error, and so should raise an exception.
            If None will use defaults defined in Transceiver method
        :type error_states: None or set(CPUState)
        :param progress_bar: Possible progress bar to update.
        :type progress_bar: ~spinn_utilities.progress_bar.ProgressBar or None
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanTimeoutException:
            If a timeout is specified and exceeded.
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.wait_for_cores_to_be_in_state(
            all_core_subsets, app_id, cpu_states, timeout,
            error_states, progress_bar)

    @classmethod
    def clear_router_diagnostic_counters(cls, x, y):
        """
        Clear router diagnostic information on a chip.

        Syntactic sugar for
        `get_transceiver().clear_router_diagnostic_counters`.

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters or a counter
            ID is out of range
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.clear_router_diagnostic_counters(x, y)

    @classmethod
    def malloc_sdram(cls, x, y, size, app_id, tag=None):
        """
        Allocates a chunk of SDRAM on a chip on the machine.

        Syntactic sugar for `get_transceiver().malloc_sdram`.

        :param int x: The x-coordinate of the chip onto which to ask for memory
        :param int y: The y-coordinate of the chip onto which to ask for memory
        :param int size: the amount of memory to allocate in bytes
        :param int app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :param int tag: the tag for the SDRAM, a 8-bit (chip-wide) tag that can
            be looked up by a SpiNNaker application to discover the address of
            the allocated block. If `0` then no tag is applied.
        :return: the base address of the allocated memory
        :rtype: int
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        """
        if cls.__data._transceiver is None:
            raise cls._exception("transceiver")
        return cls.__data._transceiver.malloc_sdram(x, y, size, app_id, tag)

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
