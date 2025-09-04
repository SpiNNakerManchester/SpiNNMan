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
    is_config_none, load_config, get_config_str_or_none)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

from spinn_machine.virtual_machine import virtual_machine_generator

from spinnman.data.spinnman_data_writer import SpiNNManDataWriter
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
        "__data_writer", )

    def __init__(
            self, data_writer_cls: Optional[Type[SpiNNManDataWriter]] = None):
        load_config()

        if data_writer_cls:
            self.__data_writer = data_writer_cls.setup()
        else:
            self.__data_writer = SpiNNManDataWriter.setup()

    @property
    def _data_writer(self) -> SpiNNManDataWriter:
        return self.__data_writer

    def _execute_get_virtual_machine(self) -> None:
        """
        Runs VirtualMachineGenerator

        Will set then "machine" and ipaddress values.
        """
        self._data_writer.set_machine(virtual_machine_generator())
        self._data_writer.set_ipaddress("virtual")

    def _do_get_allocator_data(
            self, total_run_time: Optional[float]) -> Optional[
            Tuple[str, int, Optional[str], bool, bool, Optional[Dict[XY, str]],
                  MachineAllocationController]]:
        """
        Runs, times and logs the SpallocAllocator or HBPAllocator if required.

        :param total_run_time: The total run time to request
        :return: machine name, machine version, BMP details (if any),
            reset on startup flag, auto-detect BMP, SCAMP connection details,
            boot port, allocation controller
        """
        spalloc_server = get_config_str_or_none("Machine", "spalloc_server")
        if spalloc_server:
            if is_server_address(spalloc_server):
                return self._execute_spalloc_allocate_job()
            else:
                return self._execute_spalloc_allocate_job_old()
        if not is_config_none("Machine", "remote_spinnaker_url"):
            return self._execute_hbp_allocator(total_run_time)
        return None

    def _execute_spalloc_allocate_job(self) -> Tuple[
            str, int, Optional[str], bool, bool, Dict[XY, str],
            MachineAllocationController]:
        host, version, connections, mac = spalloc_allocate_job()
        return (
            host, version, None, False, False, connections, mac)

    def _execute_spalloc_allocate_job_old(self) -> Tuple[
            str, int, Optional[str], bool, bool, Dict[XY, str],
            MachineAllocationController]:
        raise NotImplementedError()

    def _execute_hbp_allocator(
            self, total_run_time:  Optional[float]) -> Tuple[
            str, int, Optional[str], bool, bool, None,
            MachineAllocationController]:
        raise NotImplementedError()
