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

from spinn_utilities.overrides import overrides
from spinnman.data import SpiNNManDataView
from spinnman.model.enums import CPUState
from spinnman.transceiver.abstract_transceiver import AbstractTransceiver
from spinnman.transceiver.extendable_transceiver import ExtendableTransceiver


class MockableTransceiver(ExtendableTransceiver):
    """
    A based for Mock Transceivers
    """
    __slots__ = ["written_memory"]

    def __init__(self):
        self.written_memory = list()

    @overrides(AbstractTransceiver.send_sdp_message)
    def send_sdp_message(self, message, connection=None):
        pass

    @overrides(AbstractTransceiver.discover_scamp_connections)
    def discover_scamp_connections(self):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.add_scamp_connections)
    def add_scamp_connections(self, connections):
        pass

    @overrides(AbstractTransceiver.get_machine_details)
    def get_machine_details(self):
        return SpiNNManDataView.get_machine()

    @overrides(AbstractTransceiver.get_connections)
    def get_connections(self):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.ensure_board_is_ready)
    def ensure_board_is_ready(self, n_retries=5, extra_boot_values=None):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.get_cpu_infos)
    def get_cpu_infos(
            self, core_subsets=None, states=None, include=True):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.get_clock_drift)
    def get_clock_drift(self, x, y):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.read_user)
    def read_user(self, x, y, p, user):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.get_cpu_information_from_core)
    def get_cpu_information_from_core(self, x, y, p):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.get_iobuf)
    def get_iobuf(self, core_subsets=None):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.get_core_state_count)
    def get_core_state_count(self, app_id, state):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.execute_flood)
    def execute_flood(
            self, core_subsets, executable, app_id, n_bytes=None, wait=False,
            is_filename=False):
        pass

    @overrides(AbstractTransceiver.power_on)
    def power_on(self, boards=0):
        """
        Power on a set of boards in the machine.

        :param int boards: The board or boards to power on
        """
        return True

    @overrides(AbstractTransceiver.power_off_machine)
    def power_off_machine(self):
        return True

    @overrides(AbstractTransceiver.power_off)
    def power_off(self, boards=0):
        return True

    @overrides(AbstractTransceiver.read_fpga_register)
    def read_fpga_register(
            self, fpga_num, register, board=0):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.write_fpga_register)
    def write_fpga_register(self, fpga_num, register, value, board=0):
        pass

    @overrides(AbstractTransceiver.read_bmp_version)
    def read_bmp_version(self, board):
        """
        Read the BMP version.

        :param int board: which board to request the data from
        :return: the sver from the BMP
        """
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.write_memory)
    def write_memory(self, x, y, base_address, data, n_bytes=None, offset=0,
                     cpu=0, is_filename=False, get_sum=False):
        print("Doing write to", x, y)
        self.written_memory.append(
            (x, y, base_address, data, n_bytes, offset, cpu, is_filename))

    @overrides(AbstractTransceiver.write_user)
    def write_user(self, x, y, p, user, value):
        pass

    @overrides(AbstractTransceiver.read_memory)
    def read_memory(self, x, y, base_address, length, cpu=0):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.read_word)
    def read_word(self, x, y, base_address, cpu=0):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.stop_application)
    def stop_application(self, app_id):
        pass

    @overrides(AbstractTransceiver.wait_for_cores_to_be_in_state)
    def wait_for_cores_to_be_in_state(
            self, all_core_subsets, app_id, cpu_states, timeout=None,
            time_between_polls=0.1,
            error_states=frozenset({
                CPUState.RUN_TIME_EXCEPTION, CPUState.WATCHDOG}),
            counts_between_full_check=100, progress_bar=None):
        pass

    @overrides(AbstractTransceiver.send_signal)
    def send_signal(self, app_id, signal):
        pass

    @overrides(AbstractTransceiver.set_ip_tag)
    def set_ip_tag(self, ip_tag, use_sender=False):
        pass

    @overrides(AbstractTransceiver.set_reverse_ip_tag)
    def set_reverse_ip_tag(self, reverse_ip_tag):
        pass

    @overrides(AbstractTransceiver.clear_ip_tag)
    def clear_ip_tag(self, tag, board_address=None):
        pass

    @overrides(AbstractTransceiver.get_tags)
    def get_tags(self, connection=None):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.malloc_sdram)
    def malloc_sdram(self, x, y, size, app_id, tag=None):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.load_multicast_routes)
    def load_multicast_routes(self, x, y, routes, app_id):
        pass

    @overrides(AbstractTransceiver.load_fixed_route)
    def load_fixed_route(self, x, y, fixed_route, app_id):
        pass

    @overrides(AbstractTransceiver.read_fixed_route)
    def read_fixed_route(self, x, y, app_id):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.get_multicast_routes)
    def get_multicast_routes(self, x, y, app_id=None):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.clear_multicast_routes)
    def clear_multicast_routes(self, x, y):
        pass

    @overrides(AbstractTransceiver.get_router_diagnostics)
    def get_router_diagnostics(self, x, y):
        raise NotImplementedError("Needs to be mocked")

    @overrides(AbstractTransceiver.set_router_diagnostic_filter)
    def set_router_diagnostic_filter(self, x, y, position, diagnostic_filter):
        pass

    @overrides(AbstractTransceiver.clear_router_diagnostic_counters)
    def clear_router_diagnostic_counters(self, x, y):
        pass

    @overrides(AbstractTransceiver.close)
    def close(self):
        pass

    @overrides(AbstractTransceiver.control_sync)
    def control_sync(self, do_sync):
        pass

    @overrides(AbstractTransceiver.update_provenance_and_exit)
    def update_provenance_and_exit(self, x, y, p):
        pass

    @overrides(ExtendableTransceiver.bmp_connection)
    def bmp_connection(self):
        raise NotImplementedError("Needs to be mocked")

    @overrides(ExtendableTransceiver.bmp_selector)
    def bmp_selector(self):
        raise NotImplementedError("Needs to be mocked")

    @overrides(ExtendableTransceiver.scamp_connection_selector)
    def scamp_connection_selector(self):
        raise NotImplementedError("Needs to be mocked")

    @overrides(ExtendableTransceiver.where_is_xy)
    def where_is_xy(self, x, y):
        return f"Mocked {x=} {y=}"
