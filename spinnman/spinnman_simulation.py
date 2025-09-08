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
    load_config, get_config_str)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

from spinn_machine import Machine
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
            str, int, Optional[str], bool, bool, Optional[Dict[XY, str]],
            MachineAllocationController]:
        """
        Runs, times and logs the SpallocAllocator or HBPAllocator if required.

        :param total_run_time: The total run time to request
        :return: machine name, machine version, BMP details (if any),
            reset on startup flag, auto-detect BMP, SCAMP connection details,
            boot port, allocation controller
        """
        # use argument
        _ = total_run_time
        spalloc_server = get_config_str("Machine", "spalloc_server")
        if is_server_address(spalloc_server):
            host, version, connections, mac = spalloc_allocate_job()
            return (
                host, version, None, False, False, connections, mac)
        else:
            raise SpinnmanUnsupportedOperationException(
                "Only new spalloc support at the SpiNNMan level")
