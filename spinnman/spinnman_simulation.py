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
import traceback
from typing import Dict, Optional, Tuple, Type

from spinn_utilities.config_holder import (
    load_config, get_config_bool, get_config_int, get_config_str,
    get_config_str_or_none, is_config_none)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY

from spinn_machine import Machine
from spinnman.transceiver import Transceiver, transceiver_generator
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
            transceiver = self._do_transceiver_by_remote(total_run_time)
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

        return self._do_machine_by_transciever(total_run_time)

    def _do_machine_by_transciever(
            self, total_run_time: Optional[float] = 0.0, retry: int = 0) -> Machine:
        """
        Gets and if needed creates a Transceiver and then Machine

        :param total_run_time: The total run time to request
        :param retry: The number of retries attempted
        :returns: The Machine
        """
        got_transciever = False
        try:
            transceiver = self._get_transceiver()
            logger.exception(type(transceiver))
            got_transciever = True
            machine = transceiver.get_machine_details()
            self._data_writer.set_machine(machine)
            return machine
        except Exception as ex:  # pylint: disable=broad-except
            max_retry = get_config_int("Machine", "spalloc_retry")
            if retry >= max_retry:
                logger.exception(
                    "\n*****************************************************")
            logger.exception(f"Error on machine_generation {retry=}")
            logger.exception(ex)
            path = self._data_writer.get_error_file()
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"Error on machine_generation {retry=}\n")
                f.write(traceback.format_exc())
                if got_transciever:
                    logger.exception(f"{transceiver=}")
                    f.write(f"{transceiver=}")
            max_retry = get_config_int("Machine", "spalloc_retry")
            if retry >= max_retry:
                raise
        logger.info(f"Retrying machine_by_transciever  {retry=}")
        self._data_writer.clear_machine()
        return self._do_machine_by_transciever(total_run_time, retry=retry + 1)

    def _execute_get_virtual_machine(self) -> Machine:
        """
        Runs VirtualMachineGenerator

        Will set then "machine" and IP address values.
        """
        machine = virtual_machine_generator()
        self._data_writer.set_machine(machine)
        self._data_writer.set_ipaddress("virtual")
        return machine

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

        transceiver = transceiver_generator(
            bmp_details, auto_detect_bmp, None, reset_machine)
        self._data_writer.set_transceiver(transceiver)
        return transceiver

    def _do_transceiver_by_remote(
            self, total_run_time: Optional[float]) -> Transceiver:
        _ = total_run_time
        spalloc_server = get_config_str("Machine", "spalloc_server")
        if is_server_address(spalloc_server):
            transceiver, _ = self._execute_transceiver_by_spalloc()
            return transceiver
        else:
            raise SpinnmanUnsupportedOperationException(
                "Only new spalloc support at the SpiNNMan level")

    def _execute_transceiver_by_spalloc(
            self) -> Tuple[Transceiver, Dict[XY, str]]:
        """
        :return: Transceiver and connections (to write to provance)r
        """
        ipaddress, connections, controller = spalloc_allocate_job()
        self._data_writer.set_ipaddress(ipaddress)
        self._data_writer.set_allocation_controller(controller)
        if controller.can_create_transceiver():
            transceiver = controller.create_transceiver()
        else:
            transceiver = transceiver_generator(
                bmp_details=None, auto_detect_bmp=False,
                scamp_connection_data=connections,
                reset_machine_on_start_up=False)
        self._data_writer.set_transceiver(transceiver)
        return (transceiver, connections)
