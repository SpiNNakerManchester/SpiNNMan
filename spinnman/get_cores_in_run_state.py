# Copyright (c) 2017 The University of Manchester
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

"""
This is a script used to check the state of a SpiNNaker machine.
"""

import argparse
import sys
from typing import List, Optional

from spinn_utilities.config_holder import set_config
from spinn_machine import CoreSubsets, CoreSubset

from spinnman.board_test_configuration import BoardTestConfiguration
from spinnman.config_setup import unittest_setup
from spinnman.model.enums import CPUState
from spinnman.transceiver import create_transceiver_from_hostname, Transceiver

SCAMP_ID = 0
IGNORED_IDS = {SCAMP_ID, 16}  # WHY 16?


def get_cores_in_run_state(
        txrx: Transceiver, app_id: int, print_all_chips: bool) -> None:
    """
    :param txrx:
    :param app_id:
    :param print_all_chips:
    """
    count_finished = txrx.get_core_state_count(app_id, CPUState.FINISHED)
    count_run = txrx.get_core_state_count(app_id, CPUState.RUNNING)
    print(f'running: {count_run} finished: {count_finished}')

    machine = txrx.get_machine_details()
    print(f'machine width: {machine.width} height: {machine.height}')
    if print_all_chips:
        print(f'machine chips: {list(machine.chips)}')

    all_cores = []
    for chip in machine.chips:
        all_cores.append(CoreSubset(
            chip.x, chip.y, chip.placable_processors_ids))

    all_cores_subsets = CoreSubsets(core_subsets=all_cores)

    cpu_infos = txrx.get_cpu_infos(
        all_cores_subsets,
        [CPUState.FINISHED, CPUState.RUNNING, CPUState.WATCHDOG], True)
    cores_finished = cpu_infos.infos_for_state(CPUState.FINISHED)
    cores_running = cpu_infos.infos_for_state(CPUState.RUNNING)
    cores_watchdog = cpu_infos.infos_for_state(CPUState.WATCHDOG)

    for x, y, p in cores_running:
        if p not in IGNORED_IDS:
            print(f'run core: {x} {y} {p}')

    for x, y, p in cores_finished:
        print(f'finished core: {x} {y} {p}')

    for x, y, p in cores_watchdog:
        print(f'watchdog core: {x} {y} {p}')


def _make_transceiver(host: Optional[str], version: Optional[int],
                      bmp_names: Optional[str]) -> Transceiver:
    """
    :param host:
        Host to use or `None` to use test configuration for all parameters
    :param version: Board version to use (`None` defaults to 5 unless host is
        192.168.240.253 (spin 3)
    :param bmp_names: names of BMP connection
        or `None` to auto detect (if applicable)
    """
    if host is None:
        config = BoardTestConfiguration()
        config.set_up_remote_board()
        host = config.remotehost
        bmp_names = None
        auto_detect_bmp = config.auto_detect_bmp
    else:
        if version is None:
            if host == "192.168.240.253":
                version = 3
            else:
                version = 5
        auto_detect_bmp = False
        set_config("Machine", "version", str(version))

    print(f"talking to SpiNNaker system at {host}")
    # TODO https://github.com/SpiNNakerManchester/SpiNNMan/issues/423
    assert bmp_names is None
    return create_transceiver_from_hostname(
        host, bmp_connection_data=bmp_names,
        auto_detect_bmp=auto_detect_bmp)


def main(args: List[str]) -> None:
    """
    Runs the script.
    """
    unittest_setup()
    ap = argparse.ArgumentParser(
        description="Check the state of a SpiNNaker machine.")
    ap.add_argument(
        "-a", "--appid", help="the application ID to check", type=int,
        default=17)
    ap.add_argument(
        "-v", "--version", help="the version of your boards", type=int,
        default=None)
    ap.add_argument(
        "-b", "--bmp_names",
        help="the hostname or IP address of the BMP of the SpiNNaker machine "
             "to inspects",
        type=str, default=None)
    ap.add_argument(
        "-n", "--noprintchips", action="store_true", default=False,
        help=("don't print all the chips out; avoids a great deal of "
              "output for large machines"))
    ap.add_argument(
        "host", default=None, nargs='?',
        help="the hostname or IP address of the SpiNNaker machine to inspect")
    _args: argparse.Namespace = ap.parse_args(args)
    # These ought to be parsed from command line arguments
    app_id = _args.appid
    print_chips = not _args.noprintchips

    transceiver = _make_transceiver(
        _args.host, _args.version, _args.bmp_names)
    try:
        get_cores_in_run_state(transceiver, app_id, print_chips)
    finally:
        transceiver.close()


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
