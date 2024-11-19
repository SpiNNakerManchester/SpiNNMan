# Copyright (c) 2023 The University of Manchester
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
# limitations under
# return 0the License.

from typing import Dict, Iterable, Optional, Union
from spinn_utilities.overrides import overrides
from spinn_machine import CoreSubsets, Machine, virtual_machine
from spinnman.constants import N_RETRIES
from spinnman.exceptions import SpinnmanIOException
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.spinnaker_boot import SystemVariableDefinition
from spinnman.model import CPUInfos, VersionInfo
from spinnman.model.enums import CPUState
from spinnman.processes import ConnectionSelector
from .version5transceiver import Version5Transceiver


class Virtual5Transceiver(Version5Transceiver):
    """
    Overwrites the standard Version 5 Transceiver
    to intercept the sending of messages.

    This is just enough different to pass know tests.
    Extend for new tests!
    """

    @overrides(Version5Transceiver._boot_board)
    def _boot_board(self, extra_boot_values: Optional[Dict[
            SystemVariableDefinition, object]] = None) -> None:
        try:
            super()._boot_board(extra_boot_values)
        except SpinnmanIOException:
            pass

    @overrides(Version5Transceiver.read_memory)
    def read_memory(
            self, x: int, y: int, base_address: int, length: int,
            cpu: int = 0) -> bytearray:
        try:
            return super().read_memory(x, y, base_address, length, cpu)
        except SpinnmanIOException as exc:
            if (x == y == 255 and base_address == 4110450434):
                return bytearray(b'\x08\x08')
            raise NotImplementedError(
                f"Unexpected {x=} {y=} {base_address=}, {length=} {cpu=}") \
                from exc

    @overrides(Version5Transceiver._get_scamp_version)
    def _get_scamp_version(
            self, chip_x: int = AbstractSCPRequest.DEFAULT_DEST_X_COORD,
            chip_y: int = AbstractSCPRequest.DEFAULT_DEST_Y_COORD,
            connection_selector: Optional[ConnectionSelector] = None,
            n_retries: int = N_RETRIES) -> VersionInfo:
        try:
            return super()._get_scamp_version(
                chip_x, chip_y, connection_selector, n_retries)
        except SpinnmanIOException:
            version = VersionInfo(
                b'@\x00\x07\x08\xff\x00\x00\x00\x00\x00\x80\x00\x02\x00\x00\n'
                b'\x00\x00\x00\x01\xff\xffoa\xa3bSC&MP/SpiNNaker\x003.4.2\x00',
                offset=14)
            return version

    @overrides(Version5Transceiver.get_machine_details)
    def get_machine_details(self) -> Machine:
        try:
            return super().get_machine_details()
        except SpinnmanIOException:
            return virtual_machine(8, 8)

    @overrides(Version5Transceiver.get_cpu_infos)
    def get_cpu_infos(
            self, core_subsets: Optional[CoreSubsets] = None,
            states: Union[CPUState, Iterable[CPUState], None] = None,
            include: bool = True) -> CPUInfos:
        try:
            return super().get_cpu_infos(core_subsets, states, include)
        except SpinnmanIOException:
            # return an empty
            return CPUInfos()
