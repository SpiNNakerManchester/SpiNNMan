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
from contextlib import contextmanager
import io
import os
import logging
import struct
import time
from typing import Optional
from spinn_utilities.overrides import overrides
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.logger_utils import warn_once
from spinn_utilities.require_subclass import require_subclass
from spinn_machine import CoreSubsets
from spinnman.constants import (
    ROUTER_REGISTER_BASE_ADDRESS, ROUTER_FILTER_CONTROLS_OFFSET,
    ROUTER_DIAGNOSTIC_FILTER_SIZE)
from spinnman.exceptions import SpinnmanException
from spinnman.extended import (
    BMPSetLed, DeAllocSDRAMProcess, ReadADC, SetLED, WriteMemoryFloodProcess)
from spinnman.model import DiagnosticFilter
from spinnman.model.enums import CPUState
from spinnman.messages.scp.enums import Signal
from spinnman.messages.scp.impl import (
    ReadMemory, ApplicationRun)
from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.constants import SYSTEM_VARIABLE_BASE_ADDRESS
from spinnman.data import SpiNNManDataView
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.processes import (
    ConnectionSelector, GetHeapProcess, ReadMemoryProcess,
    SendSingleCommandProcess, WriteMemoryProcess)
from spinnman.transceiver.extendable_transceiver import ExtendableTransceiver

_ONE_BYTE = struct.Struct("B")
_ONE_WORD = struct.Struct("<I")

logger = FormatAdapter(logging.getLogger(__name__))


@require_subclass(ExtendableTransceiver)
class ExtendedTransceiver(object, metaclass=AbstractBase):
    """
    Allows a Transceiver to support extra method not currently needed.

    All methods here are in danger of being removed if they become too hard
    to support and many are untested so use at your own risk.
    It is undetermined if these will work with Spin2 boards.

    If any method here is considered important to keep please move it to
    Transceiver and its implementations
    """
    __slots__ = ()

    # calls many methods only reachable do to require_subclass
    # pylint: disable=no-member,assigning-non-slot
    # pylint: disable=access-member-before-definition
    # pylint: disable=attribute-defined-outside-init
    # pylint: disable=protected-access

    @abstractmethod
    def _where_is_xy(self, x: int, y: int) -> Optional[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    @overrides(ExtendableTransceiver.scamp_connection_selector)
    def scamp_connection_selector(self) -> ConnectionSelector:
        """
        Returns the scamp selector

        :rtype: AbstractMultiConnectionProcessConnectionSelector
        """
        raise NotImplementedError

    def is_connected(self, connection=None):
        """
        Determines if the board can be contacted via SCAMP

        :param Connection connection:
            The connection which is to be tested.  If `None`,
            all Scamp connections will be tested,
            and the board will be considered
            to be connected if any one connection works.
        :return: True if the board can be contacted, False otherwise
        :rtype: bool
        """
        if connection is not None:
            return connection.is_connected()
        return any(c.is_connected() and isinstance(c, SCAMPConnection)
                   for c in self.scamp_connections)

    def get_iobuf_from_core(self, x, y, p):
        """
        Get the contents of IOBUF for a given core.

        .. warning::
            This method is currently deprecated and likely to be removed.

        :param int x: The x-coordinate of the chip containing the processor
        :param int y: The y-coordinate of the chip containing the processor
        :param int p: The ID of the processor to get the IOBUF for
        :return: An IOBUF buffer
        :rtype: IOBuffer
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
        warn_once(logger, "The get_iobuf_from_core method is deprecated and "
                  "likely to be removed.")
        core_subsets = CoreSubsets()
        core_subsets.add_processor(x, y, p)
        return next(self.get_iobuf(core_subsets))

    @contextmanager
    def _chip_execute_lock(self, x, y):
        """
        Get a lock for executing an executable on a chip.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use except for execute, which is itself deprecated.

        :param int x:
        :param int y:
        """
        # Check if there is a lock for the given chip
        with self._chip_execute_lock_condition:
            chip_lock = self._chip_execute_locks[x, y]
        # Acquire the lock for the chip
        chip_lock.acquire()

        # Increment the lock counter (used for the flood lock)
        with self._chip_execute_lock_condition:
            self._n_chip_execute_locks += 1

        try:
            yield chip_lock
        finally:
            with self._chip_execute_lock_condition:
                # Release the chip lock
                chip_lock.release()
                # Decrement the lock and notify
                self._n_chip_execute_locks -= 1
                self._chip_execute_lock_condition.notify_all()

    def execute(self, x, y, processors, executable, app_id, n_bytes=None,
                wait=False):
        """
        Start an executable running on a single chip.

        .. warning::
            This method is currently deprecated and likely to be removed.

        :param int x:
            The x-coordinate of the chip on which to run the executable
        :param int y:
            The y-coordinate of the chip on which to run the executable
        :param list(int) processors:
            The cores on the chip on which to run the application
        :param executable:
            The data that is to be executed. Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A filename of a file containing the executable (in which case
              `is_filename` must be set to True)
        :type executable:
            ~io.RawIOBase or bytes or bytearray or str
        :param int app_id:
            The ID of the application with which to associate the executable
        :param int n_bytes:
            The size of the executable data in bytes. If not specified:

            * If executable is an RawIOBase, an error is raised
            * If executable is a bytearray, the length of the bytearray will
              be used
            * If executable is an int, 4 will be used
            * If executable is a str, the length of the file will be used
        :param bool wait:
            True if the binary should enter a "wait" state on loading
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the executable
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y, p does not lead to a valid core
            * If app_id is an invalid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        warn_once(logger, "The Transceiver's execute method is deprecated "
                          "likely to be removed.")
        # Lock against updates
        with self._chip_execute_lock(x, y):
            # Write the executable
            self.write_memory(
                x, y, self._EXECUTABLE_ADDRESS, executable, n_bytes=n_bytes)

            # Request the start of the executable
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(ApplicationRun(app_id, x, y, processors, wait))

    def execute_application(self, executable_targets, app_id):
        """
        Execute a set of binaries that make up a complete application on
        specified cores, wait for them to be ready and then start all of the
        binaries.

        .. note::
            This will get the binaries into c_main but will not signal the
            barrier.

        :param ExecutableTargets executable_targets:
            The binaries to be executed and the cores to execute them on
        :param int app_id: The app_id to give this application
        """
        # Execute each of the binaries and get them in to a "wait" state
        for binary in executable_targets.binaries:
            core_subsets = executable_targets.get_cores_for_binary(binary)
            self.execute_flood(core_subsets, binary, app_id, wait=True)

        # Sleep to allow cores to get going
        time.sleep(0.5)

        # Check that the binaries have reached a wait state
        count = self.get_core_state_count(app_id, CPUState.READY)
        if count < executable_targets.total_processors:
            cores_ready = self.get_cpu_infos(
                executable_targets.all_core_subsets, [CPUState.READY],
                include=False)
            if len(cores_ready) > 0:
                raise SpinnmanException(
                    f"Only {count} of {executable_targets.total_processors} "
                    "cores reached ready state: "
                    f"{cores_ready.get_status_string()}")

        # Send a signal telling the application to start
        self.send_signal(app_id, Signal.START)

    def set_led(self, led, action, board):
        """
        Set the LED state of a board in the machine.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param led:
            Number of the LED or an iterable of LEDs to set the state of (0-7)
        :type led: int or iterable(int)
        :param LEDAction action:
            State to set the LED to, either on, off or toggle
        :param board: Specifies the board to control the LEDs of. This may
            also be an iterable of multiple boards. The
            command will actually be sent to the first board in the iterable.
        :type board: int or iterable(int)
        """
        warn_once(logger, "The set_led method is deprecated and "
                  "untested due to no known use.")
        process = SendSingleCommandProcess(self.bmp_selector)
        process.execute(BMPSetLed(led, action, board))

    def read_adc_data(self, board):
        """
        Read the BMP ADC data.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param int board: which board to request the ADC data from
        :return: the FPGA's ADC data object
        :rtype: ADCInfo
        """
        warn_once(logger, "The read_adc_data method is deprecated and "
                  "untested due to no known use.")
        process = SendSingleCommandProcess(self.bmp_selector)
        response = process.execute(ReadADC(board))
        return response.adc_info  # pylint: disable=no-member

    def write_neighbour_memory(self, x, y, link, base_address, data,
                               n_bytes=None, offset=0, cpu=0):
        """
        Write to the memory of a neighbouring chip using a LINK_READ SCP
        command. If sent to a BMP, this command can be used to communicate
        with the FPGAs' debug registers.

        .. warning::
            This method is deprecated and untested due to no known use.

        :param int x:
            The x-coordinate of the chip whose neighbour is to be written to
        :param int y:
            The y-coordinate of the chip whose neighbour is to be written to
        :param int link:
            The link index to send the request to (or if BMP, the FPGA number)
        :param int base_address:
            The address in SDRAM where the region of memory is to be written
        :param data: The data to write.  Should be one of the following:

            * An instance of RawIOBase
            * A bytearray/bytes
            * A single integer; will be written in little-endian byte order
        :type data:
            ~io.RawIOBase or bytes or bytearray or int
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray, the length of the bytearray will be
              used
            * If `data` is an int, 4 will be used
        :param int offset:
            The offset where the valid data starts (if `data` is
            an int then offset will be ignored and used 0)
        :param int cpu:
            The CPU to use, typically 0 (or if a BMP, the slot number)
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
        warn_once(logger, "The write_neighbour_memory method is deprecated "
                          "and untested due to no known use.")
        process = WriteMemoryProcess(self.scamp_connection_selector)
        if isinstance(data, io.RawIOBase):
            process.write_link_memory_from_reader(
                (x, y, cpu), link, base_address, data, n_bytes)
        elif isinstance(data, int):
            data_to_write = self._ONE_WORD.pack(data)
            process.write_link_memory_from_bytearray(
                (x, y, cpu), link, base_address, data_to_write, 0, 4)
        else:
            if n_bytes is None:
                n_bytes = len(data)
            process.write_link_memory_from_bytearray(
                (x, y, cpu), link, base_address, data, offset, n_bytes)

    def read_neighbour_memory(self, x, y, link, base_address, length, cpu=0):
        """
        Read some areas of memory on a neighbouring chip using a LINK_READ
        SCP command. If sent to a BMP, this command can be used to
        communicate with the FPGAs' debug registers.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param int x:
            The x-coordinate of the chip whose neighbour is to be read from
        :param int y:
            The y-coordinate of the chip whose neighbour is to be read from
        :param int cpu:
            The CPU to use, typically 0 (or if a BMP, the slot number)
        :param int link:
            The link index to send the request to (or if BMP, the FPGA number)
        :param int base_address:
            The address in SDRAM where the region of memory to be read starts
        :param int length: The length of the data to be read in bytes
        :return: An iterable of chunks of data read in order
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
        try:
            warn_once(logger, "The read_neighbour_memory method is deprecated "
                      "and untested due to no known use.")
            process = ReadMemoryProcess(self.scamp_connection_selector)
            return process.read_link_memory(
                (x, y, cpu), link, base_address, length)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    def _get_next_nearest_neighbour_id(self):
        with self._nearest_neighbour_lock:
            next_nearest_neighbour_id = (self._nearest_neighbour_id + 1) % 127
            self._nearest_neighbour_id = next_nearest_neighbour_id
        return next_nearest_neighbour_id

    def write_memory_flood(
            self, base_address, data, n_bytes=None, offset=0,
            is_filename=False):
        """
        Write to the SDRAM of all chips.

        :param int base_address:
            The address in SDRAM where the region of memory is to be written
        :param data:
            The data that is to be written.  Should be one of the following:

            * An instance of RawIOBase
            * A byte-string
            * A single integer
            * A file name of a file to read (in which case `is_filename`
              should be set to True)
        :type data:
            ~io.RawIOBase or bytes or bytearray or int or str
        :param int n_bytes:
            The amount of data to be written in bytes.  If not specified:

            * If `data` is an RawIOBase, an error is raised
            * If `data` is a bytearray or bytes, the length of the bytearray
              will be used
            * If `data` is an int, 4 will be used
            * If `data` is a str, the size of the file will be used
        :param int offset:
            The offset where the valid data starts; if `data` is
            an int, then the offset will be ignored and 0 is used.
        :param bool is_filename:
            True if `data` should be interpreted as a file name
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the executable
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If one of the specified chips is not valid
            * If `app_id` is an invalid application ID
            * If a packet is received that has invalid parameters
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        process = WriteMemoryFloodProcess(self._scamp_connection_selector)
        # Ensure only one flood fill occurs at any one time
        with self._flood_write_lock:
            # Start the flood fill
            nearest_neighbour_id = self._get_next_nearest_neighbour_id()
            if isinstance(data, io.RawIOBase):
                process.write_memory_from_reader(
                    nearest_neighbour_id, base_address, data, n_bytes)
            elif isinstance(data, str) and is_filename:
                if n_bytes is None:
                    n_bytes = os.stat(data).st_size
                with open(data, "rb") as reader:
                    process.write_memory_from_reader(
                        nearest_neighbour_id, base_address, reader, n_bytes)
            elif isinstance(data, int):
                data_to_write = self._ONE_WORD.pack(data)
                process.write_memory_from_bytearray(
                    nearest_neighbour_id, base_address, data_to_write, 0)
            else:
                if n_bytes is None:
                    n_bytes = len(data)
                process.write_memory_from_bytearray(
                    nearest_neighbour_id, base_address, data, offset, n_bytes)

    def set_leds(self, x, y, cpu, led_states):
        """
        Set LED states.

        .. warning::
            The set_leds is deprecated and untested due to no known use.

        :param int x: The x-coordinate of the chip on which to set the LEDs
        :param int y: The x-coordinate of the chip on which to set the LEDs
        :param int cpu: The CPU of the chip on which to set the LEDs
        :param dict(int,int) led_states:
            A dictionary mapping SetLED index to state with
            0 being off, 1 on and 2 inverted.
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
            warn_once(logger, "The set_leds is deprecated and "
                      "untested due to no known use.")
            process = SendSingleCommandProcess(self._scamp_connection_selector)
            process.execute(SetLED(x, y, cpu, led_states))
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    def free_sdram(self, x, y, base_address):
        """
        Free allocated SDRAM.

        .. warning::
            This method is currently deprecated and likely to be removed.

        :param int x: The x-coordinate of the chip onto which to ask for memory
        :param int y: The y-coordinate of the chip onto which to ask for memory
        :param int base_address: The base address of the allocated memory
        """
        try:
            warn_once(logger, "The free_sdram method is deprecated and "
                      "likely to be removed.")
            process = DeAllocSDRAMProcess(self._scamp_connection_selector)
            process.de_alloc_sdram(x, y, base_address)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    def free_sdram_by_app_id(self, x, y, app_id):
        """
        Free all SDRAM allocated to a given app ID.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param int x: The x-coordinate of the chip onto which to ask for memory
        :param int y: The y-coordinate of the chip onto which to ask for memory
        :param int app_id: The app ID of the allocated memory
        :return: The number of blocks freed
        :rtype: int
        """
        try:
            warn_once(logger, "The free_sdram_by_app_id method is deprecated "
                              "and untested due to no known use.")
            process = DeAllocSDRAMProcess(self._scamp_connection_selector)
            process.de_alloc_sdram(x, y, app_id)
            return process.no_blocks_freed
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    def get_router_diagnostic_filter(
            self, x: int, y: int, position: int) -> DiagnosticFilter:
        """
        Gets a router diagnostic filter from a router.

        :param int x:
            the X address of the router from which this filter is being
            retrieved
        :param int y:
            the Y address of the router from which this filter is being
            retrieved
        :param int position:
            the position in the list of filters to read the information from
        :return: The diagnostic filter read
        :rtype: DiagnosticFilter
        :raise SpinnmanIOException:
            * If there is an error communicating with the board
            * If there is an error reading the data
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            * If x, y does not lead to a valid chip
            * If a packet is received that has invalid parameters
            * If position is less than 0 or more than 15
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        try:
            memory_position = (
                ROUTER_REGISTER_BASE_ADDRESS + ROUTER_FILTER_CONTROLS_OFFSET +
                position * ROUTER_DIAGNOSTIC_FILTER_SIZE)

            process: SendSingleCommandProcess = SendSingleCommandProcess(
                self.scamp_connection_selector)
            response = process.execute(
                ReadMemory((x, y, 0), memory_position, 4))
            return DiagnosticFilter.read_from_int(_ONE_WORD.unpack_from(
                response.data, response.offset)[0])
            # pylint: disable=no-member
        except Exception:
            logger.info(self._where_is_xy(x, y))
            raise

    @property
    def number_of_boards_located(self):
        """
        The number of boards currently configured.

        .. warning::
            This property is currently deprecated and likely to be removed.

        :rtype: int
        """
        warn_once(logger, "The number_of_boards_located method is deprecated "
                          "and likely to be removed.")
        if self.bmp_connection is not None:
            return max(1, len(self.bmp_connection.boards))
        else:
            # if no BMPs are available, then there's still at least one board
            return 1

    def get_heap(self, x, y, heap=SystemVariableDefinition.sdram_heap_address):
        """
        Get the contents of the given heap on a given chip.

        :param int x: The x-coordinate of the chip
        :param int y: The y-coordinate of the chip
        :param SystemVariableDefinition heap:
            The SystemVariableDefinition which is the heap to read
        :rtype: list(HeapElement)
        """
        try:
            process = GetHeapProcess(self.scamp_connection_selector)
            return process.get_heap((x, y), heap)
        except Exception:
            logger.info(self.where_is_xy(x, y))
            raise

    def __set_watch_dog_on_chip(self, x, y, watch_dog):
        """
        Enable, disable or set the value of the watch dog timer on a
        specific chip.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param int x: chip X coordinate to write new watchdog parameter to
        :param int y: chip Y coordinate to write new watchdog parameter to
        :param watch_dog:
            Either a Boolean indicating whether to enable (True) or
            disable (False) the watchdog timer, or an int value to set the
            timer count to
        :type watch_dog: bool or int
        """
        # build what we expect it to be
        warn_once(logger, "The set_watch_dog_on_chip method is deprecated "
                          "and untested due to no known use.")
        value_to_set = watch_dog
        watchdog = SystemVariableDefinition.software_watchdog_count
        if isinstance(watch_dog, bool):
            value_to_set = watchdog.default if watch_dog else 0

        # build data holder
        data = _ONE_BYTE.pack(value_to_set)

        # write data
        address = SYSTEM_VARIABLE_BASE_ADDRESS + watchdog.offset
        self.write_memory(x=x, y=y, base_address=address, data=data)

    def set_watch_dog(self, watch_dog):
        """
        Enable, disable or set the value of the watch dog timer.

        .. warning::
            This method is currently deprecated and untested as there is no
            known use. Same functionality provided by ybug and bmpc.
            Retained in case needed for hardware debugging.

        :param watch_dog:
            Either a Boolean indicating whether to enable (True) or
            disable (False) the watch dog timer, or an int value to set the
            timer count to.
        :type watch_dog: bool or int
        """
        warn_once(logger, "The set_watch_dog method is deprecated and "
                          "untested due to no known use.")
        for x, y in SpiNNManDataView.get_machine().chip_coordinates:
            self.__set_watch_dog_on_chip(x, y, watch_dog)
