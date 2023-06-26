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
    def read_clock_drift(cls, x, y):
        """
        Get the clock drift

        Syntactic sugar for `get_transceiver().get_core_state_count`.

        :param int x: The x-coordinate of the chip to get drift for
        :param int y: The y-coordinate of the chip to get drift for
        :rtype: int
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        """
        try:
            return cls.__data._transceiver.get_clock_drift(x, y)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
           if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
           raise

    @classmethod
    def read_fixed_route(cls, x, y, app_id):
        """
        Reads a fixed route routing table entry from a chip's router.

        Syntactic sugar for `get_transceiver().read_fixed_route`.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param int app_id:
            The ID of the application with which to associate the
            routes.  If not specified, defaults to 0.
        :return: the route as a fixed route entry
        """
        try:
            return cls.__data._transceiver.read_fixed_route(x, y, app_id)
        except AttributeError as ex:
           if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
           raise

    @classmethod
    def read_iobuf(cls, core_subsets=None):
        """
        Get the contents of the IOBUF buffer for a number of processors.

        Syntactic sugar for `get_transceiver().read_iobuf`.

        :param ~spinn_machine.CoreSubsets core_subsets:
            A set of chips and cores from which to get the buffers. If not
            specified, the buffers from all of the cores on all of the chips
            on the board are obtained.
        :return: An iterable of the buffers, which may not be in the order
            of core_subsets
        :rtype: iterable(IOBuffer)
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If chip_and_cores contains invalid items
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.get_iobuf(core_subsets)
        except AttributeError as ex:
           if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
           raise

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
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def read_multicast_routes(cls, x, y, app_id=None):
        """
        Get the current multicast routes set up on a chip.

        Syntactic sugar for `get_transceiver().get_multicast_routes`.

        :param int x:
            The x-coordinate of the chip from which to get the routes
        :param int y:
            The y-coordinate of the chip from which to get the routes
        :param int app_id:
            The ID of the application to filter the routes for. If
            not specified, will return all routes
        :return: An iterable of multicast routes
        :rtype: list(~spinn_machine.MulticastRoutingEntry)
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable

        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.get_multicast_routes(x, y, app_id)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def read_router_diagnostics(cls, x, y):
        """
        Get router diagnostic information from a chip.

        Syntactic sugar for `get_transceiver().get_router_diagnostics`.

        :param int x:
            The x-coordinate of the chip from which to get the information
        :param int y:
            The y-coordinate of the chip from which to get the information
        :return: The router diagnostic information
        :rtype: RouterDiagnostics
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.get_router_diagnostics(x, y)
        except AttributeError as ex:
               if cls.__data._transceiver is None:
                    raise cls._exception("transceiver") from ex
               raise

    @classmethod
    def read_core_tags(cls, connection=None):
        """
        Get the current set of tags that have been set on the board.

        Syntactic sugar for `get_transceiver().get_tags`.

        :param AbstractSCPConnection connection:
            Connection from which the tags should be received.
            If not specified, all AbstractSCPConnection connections will be
            queried and the response will be combined.
        :return: An iterable of tags
        :rtype: iterable(~spinn_machine.tags.AbstractTag)
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the connection cannot send SDP messages
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.get_tags(connection)
        except AttributeError as ex:
               if cls.__data._transceiver is None:
                    raise cls._exception("transceiver") from ex
               raise

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
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def read_cores_not_in_state(cls, all_core_subsets, states):
        """
        Get all cores that are in a given state or set of states.

        Syntactic sugar for `get_transceiver().get_cores_not_in_state`.

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
            return cls.__data._transceiver.get_cores_not_in_state(
                all_core_subsets, states)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
           if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
           raise

    @classmethod
    def write_fixed_route(cls, x, y, fixed_route, app_id):
        """
        Loads a fixed route routing table entry onto a chip's router.

        Syntactic sugar for `get_transceiver().write_fixed_route`.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param ~spinn_machine.FixedRouteEntry fixed_route:
            the route for the fixed route entry on this chip
        :param int app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If any of the routes are invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.load_fixed_route(
                x, y, fixed_route, app_id)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_flood(
            cls, core_subsets, executable, app_id, n_bytes=None, wait=False,
            is_filename=False):
        """
        Start an executable running on multiple places on the board.  This
        will be optimised based on the selected cores, but it may still
        require a number of communications with the board to execute.

        Syntactic sugar for `get_transceiver().execute_flood`.

        :param ~spinn_machine.CoreSubsets core_subsets:
            Which cores on which chips to start the executable
        :param executable:
            The data that is to be executed. Should be one of the following:

            * An instance of RawIOBase
            * A bytearray
            * A filename of an executable (in which case `is_filename` must be
              set to True)
        :type executable:
            ~io.RawIOBase or bytes or bytearray or str
        :param int app_id:
            The ID of the application with which to associate the executable
        :param int n_bytes:
            The size of the executable data in bytes. If not specified:

            * If `executable` is an RawIOBase, an error is raised
            * If `executable` is a bytearray, the length of the bytearray will
              be used
            * If `executable` is an int, 4 will be used
            * If `executable` is a str, the length of the file will be used
        :param bool wait:
            True if the processors should enter a "wait" state on loading
        :param bool is_filename: True if the data is a filename
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the executable
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of the specified cores is not valid
            * If `app_id` is an invalid application ID
            * If a packet is received that has invalid parameters
            * If `executable` is an RawIOBase but `n_bytes` is not specified
            * If `executable` is an int and `n_bytes` is more than 4
            * If `n_bytes` is less than 0
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.execute_flood(
                core_subsets, executable, app_id, n_bytes, wait, is_filename)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_ip_tag(cls, ip_tag, use_sender=False):
        """
        Set up an IP tag.

        Syntactic sugar for `get_transceiver().set_ip_tag`.

        :param ~spinn_machine.tags.IPTag ip_tag:
            The tag to set up.

            .. note::
                `board_address` can be `None`, in which case, the tag will be
                assigned to all boards.
        :param bool use_sender:
            Optionally use the sender host and port instead of
            the given host and port in the tag
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the IP tag fields are incorrect
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.set_ip_tag(ip_tag, use_sender)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_reverse_ip_tag(cls, reverse_ip_tag):
        """
        Set up a reverse IP tag.

        Syntactic sugar for `get_transceiver().set_reverse_ip_tag`.

        :param ~spinn_machine.tags.ReverseIPTag reverse_ip_tag:
            The reverse tag to set up.

            .. note::
                The `board_address` field can be `None`, in which case, the tag
                will be assigned to all boards.
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the reverse IP tag fields are incorrect
            * If a packet is received that has invalid parameters
            * If the UDP port is one that is already used by SpiNNaker for
                system functions
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.set_reverse_ip_tag(reverse_ip_tag)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_clear_ip_tag(cls, tag, board_address=None):
        """
        Clear the setting of an IP tag.

        Syntactic sugar for `get_transceiver().clear_ip_tag`.

        :param int tag: The tag ID
        :param str board_address:
            Board address where the tag should be cleared.
            If not specified, all AbstractSCPConnection connections will send
            the message to clear the tag
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If the tag is not a valid tag
            * If the connection cannot send SDP messages
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.clear_ip_tag(tag, board_address)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.write_memory(
                x, y, base_address, data, n_bytes, offset, cpu, is_filename)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_clear_multicast_routes(cls, x, y):
        """
        Remove all the multicast routes on a chip.

        Syntactic sugar for `get_transceiver().clear_multicast_routes`.

        :param int x: The x-coordinate of the chip on which to clear the routes
        :param int y: The y-coordinate of the chip on which to clear the routes
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.clear_multicast_routes(x, y)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_multicast_routes(cls, x, y, routes, app_id):
        """
        Load a set of multicast routes on to a chip.

        Syntactic sugar for `get_transceiver().load_multicast_routes`.

        :param int x:
            The x-coordinate of the chip onto which to load the routes
        :param int y:
            The y-coordinate of the chip onto which to load the routes
        :param iterable(~spinn_machine.MulticastRoutingEntry) routes:
            An iterable of multicast routes to load
        :param int app_id: The ID of the application with which to associate
            the routes.  If not specified, defaults to 0.
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If any of the routes are invalid
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.load_multicast_routes(
                x, y, routes, app_id)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

    @classmethod
    def write_router_diagnostic_filter(
            cls, x, y, position, diagnostic_filter):
        """
        Sets a router diagnostic filter in a router.

        Syntactic sugar for `get_transceiver().set_router_diagnostic_filter`.

        :param int x:
            The X address of the router in which this filter is being set.
        :param int y:
            The Y address of the router in which this filter is being set.
        :param int position:
            The position in the list of filters where this filter is to be
            added.
        :param DiagnosticFilter diagnostic_filter:
            The diagnostic filter being set in the placed, between 0 and 15.

            .. note::
                Positions 0 to 11 are used by the default filters,
                and setting these positions will result in a warning.
        :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
            If the transceiver is currently unavailable
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the data
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y does not lead to a valid chip
            * If position is less than 0 or more than 15
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            return cls.__data._transceiver.set_router_diagnostic_filter(
                x, y, position, diagnostic_filter)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.send_signal(app_id, signal)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.stop_application(app_id)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.update_provenance_and_exit(x, y, p)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.wait_for_cores_to_be_in_state(
                all_core_subsets, app_id, cpu_states, timeout,
                error_states, progress_bar)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.clear_router_diagnostic_counters(
                x, y)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
        try:
            return cls.__data._transceiver.malloc_sdram(
                x, y, size, app_id, tag)
        except AttributeError as ex:
            if cls.__data._transceiver is None:
                raise cls._exception("transceiver") from ex
            raise

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
