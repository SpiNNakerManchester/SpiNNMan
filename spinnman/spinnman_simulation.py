# Copyright (c) 2025 The University of Manchester
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
import re
from typing import Dict, Optional, Tuple, Type

from spinn_utilities.config_holder import (
    load_config, get_config_bool, get_config_str, get_config_str_or_none,
    is_config_none)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

from spinn_machine import Machine
from spinnman.transceiver import Transceiver
from spinnman.transceiver_generator import transciever_generator
from spinn_machine.virtual_machine import virtual_machine_generator

from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
from spinnman.exceptions import SpinnmanUnsupportedOperationException
from spinnman.spalloc import (
    is_server_address, MachineAllocationController)
from spinnman.spalloc.spalloc_allocator import spalloc_allocate_job

logger = FormatAdapter(logging.getLogger(__name__))

SHARED_PATH = re.compile(r".*\/shared\/([^\/]+)")
SHARED_GROUP = 1
SHARED_WITH_PATH = re.compile(r".*\/Shared with (all|groups|me)\/([^\/]+)")
SHARED_WITH_GROUP = 2


class SpiNNManSimulation(object):
    """
    The SpiNNMan level part of the simulation interface.
    """

    __slots__ = (
        # The writer and therefore view of the global data
        # access this via the property _data_writer to get the type correct
        "_untyped_data_writer", )

    def __init__(
            self, data_writer_cls: Optional[Type[SpiNNManDataWriter]] = None):
        """
        :param data_writer_cls:
            Class of the DataWriter used to store the global data
        """
        load_config()

        if data_writer_cls:
            self._untyped_data_writer = data_writer_cls.setup()
        else:
            self._untyped_data_writer = SpiNNManDataWriter.setup()

    @property
    def _data_writer(self) -> SpiNNManDataWriter:
        return self._untyped_data_writer

    def get_machine(self) -> Machine:
        """
        Get the Machine. Creating it if necessary.

        :returns: The Machine now stored in the DataView
        """
        return self._get_known_machine()

    def _get_transceiver(
            self, total_run_time: Optional[float] = 0.0, ) -> Transceiver:
        """
        Creates a Transceiver

        :param total_run_time: The total run time to request
        :return: The Transceiver
        """
        if self._data_writer.has_transceiver():
            transceiver = self._data_writer.get_transceiver()
        elif not is_config_none("Machine", "machine_name"):
            transceiver = self._execute_tranceiver_by_name()
        else:
            transceiver = self._do_allocate_transceiver(total_run_time)
        return transceiver

    def _get_known_machine(
            self, total_run_time: Optional[float] = 0.0) -> Machine:
        """
        Gets and if needed creates a Machine

        :param total_run_time: The total run time to request
        :returns: The Machine
        """
        if self._data_writer.has_machine():
            return self._data_writer.get_machine()

        if get_config_bool("Machine", "virtual_board"):
            return self._execute_get_virtual_machine()

        transceiver = self._get_transceiver()
        machine = transceiver.get_machine_details()
        self._data_writer.set_machine(machine)
        return machine

    def _execute_get_virtual_machine(self) -> Machine:
        """
        Runs VirtualMachineGenerator

        Will set then "machine" and IP address values.
        """
        machine = virtual_machine_generator()
        self._data_writer.set_machine(machine)
        self._data_writer.set_ipaddress("virtual")
        return machine

    def _do_get_allocator_data(
            self, total_run_time: Optional[float]) -> Tuple[
            str, Optional[str], bool, bool, Optional[Dict[XY, str]],
            MachineAllocationController]:
        """
        Runs, times and logs the SpallocAllocator or HBPAllocator if required.

        :param total_run_time: The total run time to request
        :return: machine name, BMP details (if any),
            reset on startup flag, auto-detect BMP, SCAMP connection details,
            boot port, allocation controller
        """
        # use argument
        _ = total_run_time
        spalloc_server = get_config_str("Machine", "spalloc_server")
        if is_server_address(spalloc_server):
            host, connections, mac = spalloc_allocate_job()
            return (
                host, None, False, False, connections, mac)
        else:
            raise SpinnmanUnsupportedOperationException(
                "Only new spalloc support at the SpiNNMan level")

    def _execute_tranceiver_by_name(self) -> Transceiver:
        """
        Runs getting the Transceiver using machine_name.

        Will create and set "transceiver" to the View

        :returns: The Tranceiver
        :raises ConfigException: if machine_name is not set in the cfg
        """
        machine_name = get_config_str("Machine", "machine_name")
        self._data_writer.set_ipaddress(machine_name)
        bmp_details = get_config_str_or_none("Machine", "bmp_names")
        auto_detect_bmp = get_config_bool("Machine", "auto_detect_bmp")
        reset_machine = get_config_bool(
            "Machine", "reset_machine_on_startup")

        transceiver = transciever_generator(
            bmp_details, auto_detect_bmp, None, reset_machine)
        self._data_writer.set_transceiver(transceiver)
        return transceiver

    def _do_allocate_transceiver(self, total_run_time: Optional[float],
                                 retry: int = 0) -> Transceiver:
        """
        Combines execute allocator and execute machine generator

        This allows allocator to be run again if it is useful to do so

        :param total_run_time: The total run time to request
        :returns: Machine created
        """
        # Used variable only needed by super class
        _ = retry
        allocator_data = self._do_get_allocator_data(total_run_time)
        return self._execute_machine_generator(allocator_data)

    def _execute_transceiver_generator(self, allocator_data: Tuple[
            str, Optional[str], bool, bool, Optional[Dict[XY, str]],
            MachineAllocationController]) -> Transceiver:
        """
        Runs the TranceiverGenerator based on allocator data.

        May set the "machine" value if not already set

        :param allocator_data:
            (machine name, machine version, BMP details (if any),
            reset on startup flag, auto-detect BMP, SCAMP connection details,
            boot port, allocation controller)
        :returns: Tranceiver created
        """
        (ipaddress, bmp_details, reset_machine, auto_detect_bmp,
            scamp_connection_data, machine_allocation_controller
            ) = allocator_data
        self._data_writer.set_ipaddress(ipaddress)
        self._data_writer.set_allocation_controller(
            machine_allocation_controller)

        transceiver = transciever_generator(
            bmp_details, auto_detect_bmp or False, scamp_connection_data,
            reset_machine or False)
        self._data_writer.set_transceiver(transceiver)
        return transceiver

