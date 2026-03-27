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

from typing import (
    BinaryIO, Collection, Dict, FrozenSet, Iterable,
    List, Optional, Set, Tuple, Union)
from spinn_utilities.overrides import overrides
from spinn_utilities.progress_bar import ProgressBar
from spinn_utilities.typing.coords import XY
from spinn_machine import (
    CoreSubsets, Machine, MulticastRoutingEntry, RoutingEntry)
from spinn_machine.tags import AbstractTag, IPTag, ReverseIPTag
from spinnman.data import SpiNNManDataView
from spinnman.connections.abstract_classes import Connection
from spinnman.connections.udp_packet_connections import BMPConnection
from spinnman.connections.udp_packet_connections import (
    SCAMPConnection, SDPConnection)
from spinnman.processes import ConnectionSelector, FixedConnectionSelector
from spinnman.messages.scp.enums import Signal
from spinnman.messages.sdp import SDPMessage
from spinnman.model import (
    CPUInfos, DiagnosticFilter, IOBuffer, RouterDiagnostics,
    VersionInfo)
from spinnman.model.enums import CPUState, UserRegister
from spinnman.transceiver.transceiver import Transceiver
from spinnman.transceiver.extendable_transceiver import ExtendableTransceiver
from spinnman.processes import MostDirectConnectionSelector


class MockableTransceiver(ExtendableTransceiver):
    """
    A based for Mock Transceivers
    """
    __slots__ = ["written_memory"]

    def __init__(self) -> None:
        super().__init__()
        self.written_memory: List[
            Tuple[int, int, int, Union[BinaryIO, bytes, int, str],
                  Optional[int], int, int]] = []

    @overrides(Transceiver.send_sdp_message)
    def send_sdp_message(self, message: SDPMessage,
                         connection: Optional[SDPConnection] = None) -> None:
        pass

    @overrides(Transceiver.discover_scamp_connections)
    def discover_scamp_connections(self) -> None:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.add_scamp_connections)
    def add_scamp_connections(self, connections: Dict[XY, str]) -> None:
        pass

    @overrides(Transceiver.get_machine_details)
    def get_machine_details(self) -> Machine:
        return SpiNNManDataView.get_machine()

    @overrides(Transceiver.get_connections)
    def get_connections(self) -> Set[Connection]:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_cpu_infos)
    def get_cpu_infos(
            self, core_subsets: Optional[CoreSubsets] = None,
            states: Union[CPUState, Iterable[CPUState], None] = None,
            include: bool = True) -> CPUInfos:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_clock_drift)
    def get_clock_drift(self, x: int, y: int) -> float:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.read_user)
    def read_user(self, x: int, y: int, p: int, user: UserRegister) -> int:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.add_cpu_information_from_core)
    def add_cpu_information_from_core(
            self, cpu_infos: CPUInfos, x: int, y: int, p: int,
            states: Iterable[CPUState]) -> None:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_region_base_address)
    def get_region_base_address(self, x: int, y: int, p: int) -> int:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_iobuf)
    def get_iobuf(self, core_subsets: Optional[CoreSubsets] = None
                  ) -> Iterable[IOBuffer]:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_core_state_count)
    def get_core_state_count(
            self, app_id: int, state: CPUState,
            xys: Optional[Iterable[Tuple[int, int]]] = None) -> int:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.execute_flood)
    def execute_flood(
            self, core_subsets: CoreSubsets,
            executable: Union[BinaryIO, bytes, str], app_id: int, *,
            n_bytes: Optional[int] = None, wait: bool = False) -> None:
        pass

    @overrides(Transceiver.read_fpga_register)
    def read_fpga_register(
            self, fpga_num: int, register: int, board: int = 0) -> int:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.write_fpga_register)
    def write_fpga_register(self, fpga_num: int, register: int, value: int,
                            board: int = 0) -> None:
        pass

    @overrides(Transceiver.read_bmp_version)
    def read_bmp_version(self, board: int) -> VersionInfo:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.write_memory)
    def write_memory(
            self, x: int, y: int, base_address: int,
            data: Union[BinaryIO, bytes, int, str], *,
            n_bytes: Optional[int] = None, offset: int = 0, cpu: int = 0,
            get_sum: bool = False) -> Tuple[int, int]:
        print("Doing write to", x, y)
        self.written_memory.append(
            (x, y, base_address, data, n_bytes, offset, cpu))
        # Hope the return is never used as it will be wrong
        return (-1, -1)

    @overrides(Transceiver.write_user)
    def write_user(self, x: int, y: int, p: int, user: UserRegister,
                   value: int) -> None:
        pass

    @overrides(Transceiver.read_memory)
    def read_memory(
            self, x: int, y: int, base_address: int, length: int,
            cpu: int = 0) -> bytearray:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.read_word)
    def read_word(
            self, x: int, y: int, base_address: int, cpu: int = 0) -> int:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.stop_application)
    def stop_application(self, app_id: int) -> None:
        pass

    @overrides(Transceiver.wait_for_cores_to_be_in_state)
    def wait_for_cores_to_be_in_state(
            self, all_core_subsets: CoreSubsets, app_id: int,
            cpu_states: Union[CPUState, Iterable[CPUState]], *,
            timeout: Optional[float] = None,
            time_between_polls: float = 0.1,
            error_states: FrozenSet[CPUState] = frozenset((
                CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG)),
            counts_between_full_check: int = 100,
            progress_bar: Optional[ProgressBar] = None) -> None:
        pass

    @overrides(Transceiver.send_signal)
    def send_signal(self, app_id: int, signal: Signal) -> None:
        pass

    @overrides(Transceiver.set_ip_tag)
    def set_ip_tag(self, ip_tag: IPTag, use_sender: bool = False) -> None:
        pass

    @overrides(Transceiver.set_reverse_ip_tag)
    def set_reverse_ip_tag(self, reverse_ip_tag: ReverseIPTag) -> None:
        pass

    @overrides(Transceiver.clear_ip_tag)
    def clear_ip_tag(
            self, tag: int, board_address: Optional[str] = None) -> None:
        pass

    @overrides(Transceiver.get_tags)
    def get_tags(self, connection: Optional[SCAMPConnection] = None
                 ) -> Iterable[AbstractTag]:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.malloc_sdram)
    def malloc_sdram(
            self, x: int, y: int, size: int, app_id: int, tag: int = 0) -> int:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.load_multicast_routes)
    def load_multicast_routes(
            self, x: int, y: int, routes: Collection[MulticastRoutingEntry],
            app_id: int) -> None:
        pass

    @overrides(Transceiver.load_fixed_route)
    def load_fixed_route(self, x: int, y: int, fixed_route: RoutingEntry,
                         app_id: int) -> None:
        pass

    @overrides(Transceiver.read_fixed_route)
    def read_fixed_route(self, x: int, y: int, app_id: int) -> RoutingEntry:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_multicast_routes)
    def get_multicast_routes(
            self, x: int, y: int,
            app_id: Optional[int] = None) -> List[MulticastRoutingEntry]:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.clear_multicast_routes)
    def clear_multicast_routes(self, xy: Optional[XY] = None) -> None:
        pass

    @overrides(Transceiver.get_router_diagnostics)
    def get_router_diagnostics(self, x: int, y: int) -> RouterDiagnostics:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.get_scamp_connection_selector)
    def get_scamp_connection_selector(self) -> MostDirectConnectionSelector:
        raise NotImplementedError("Needs to be mocked")

    @overrides(Transceiver.set_router_diagnostic_filter)
    def set_router_diagnostic_filter(
            self, x: int, y: int, position: int,
            diagnostic_filter: DiagnosticFilter) -> None:
        pass

    @overrides(Transceiver.clear_router_diagnostic_counters)
    def clear_router_diagnostic_counters(
            self, xy: Optional[XY] = None) -> None:
        pass

    @overrides(Transceiver.close)
    def close(self) -> None:
        pass

    @overrides(Transceiver.control_sync)
    def control_sync(self, do_sync: bool) -> None:
        pass

    @overrides(Transceiver.update_provenance_and_exit)
    def update_provenance_and_exit(self, x: int, y: int, p: int) -> None:
        pass

    @overrides(Transceiver.send_chip_update_provenance_and_exit)
    def send_chip_update_provenance_and_exit(
            self, x: int, y: int, p: int) -> None:
        pass

    @property
    @overrides(ExtendableTransceiver.bmp_selector)
    def bmp_selector(self) -> Optional[FixedConnectionSelector[BMPConnection]]:
        raise NotImplementedError("Needs to be mocked")

    @property
    @overrides(ExtendableTransceiver.scamp_connection_selector)
    def scamp_connection_selector(self) -> ConnectionSelector:
        raise NotImplementedError("Needs to be mocked")

    @overrides(ExtendableTransceiver.ensure_board_is_ready)
    def ensure_board_is_ready(self) -> None:
        pass
