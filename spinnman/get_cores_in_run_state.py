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

import sys
import argparse
from spinnman.transceiver import create_transceiver_from_hostname
from spinn_machine import CoreSubsets, CoreSubset
from spinnman.model.enums import CPUState

SCAMP_ID = 0
IGNORED_IDS = {SCAMP_ID, 16}  # WHY 16?


def get_cores_in_run_state(txrx, app_id, print_all_chips):
    """
    :param Transceiver txrx:
    :param int app_id:
    :param bool print_all_chips:
    """
    count_finished = txrx.get_core_state_count(app_id, CPUState.FINISHED)
    count_run = txrx.get_core_state_count(app_id, CPUState.RUNNING)
    print('running: {} finished: {}'.format(count_run, count_finished))

    machine = txrx.get_machine_details()
    print(f'machine width: {machine.width} height: {machine.height}')
    if print_all_chips:
        print('machine chips: {}'.format(list(machine.chips)))

    all_cores = []
    for chip in machine.chips:
        all_cores.append(CoreSubset(chip.x, chip.y, range(1, 17)))

    all_cores = CoreSubsets(core_subsets=all_cores)

    cores_finished = txrx.get_cores_in_state(all_cores, CPUState.FINISHED)
    cores_running = txrx.get_cores_in_state(all_cores, CPUState.RUNNING)
    cores_watchdog = txrx.get_cores_in_state(all_cores, CPUState.WATCHDOG)

    for (x, y, p), _ in cores_running:
        if p not in IGNORED_IDS:
            print('run core: {} {} {}'.format(x, y, p))

    for (x, y, p), _ in cores_finished:
        print('finished core: {} {} {}'.format(x, y, p))

    for (x, y, p), _ in cores_watchdog:
        print('watchdog core: {} {} {}'.format(x, y, p))


def _make_transceiver(host, version, bmp_names):
    """
    :param host: Most to use or `None` to use test config for all params
    :type host: str or None
    :param version: Board version to use (`None` defaults to 5 unless host is
        192.168.240.253 (spin 3)
    :type version: int or None
    :param bmp: bmp connection or `None` to auto detect (if applicable)
    :type bmp: str or None
    :rtype: Transceiver
    """
    if host is None:
        try:
            from board_test_configuration import BoardTestConfiguration
            config = BoardTestConfiguration()
        except ImportError:
            print("cannot read board test configuration")
            sys.exit(1)
        config.set_up_remote_board()
        host = config.remotehost
        version = config.board_version
        bmp_names = config.bmp_names
        auto_detect_bmp = config.auto_detect_bmp
    else:
        if version is None:
            if host == "192.168.240.253":
                version = 3
            else:
                version = 5
        auto_detect_bmp = False

    print("talking to SpiNNaker system at {}".format(host))
    return create_transceiver_from_hostname(
        host, version,
        bmp_connection_data=bmp_names,
        auto_detect_bmp=auto_detect_bmp)


def main(args):
    """
    Runs the script.
    """
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
    args = ap.parse_args(args)
    # These ought to be parsed from command line arguments
    app_id = args.appid
    print_chips = not args.noprintchips

    transceiver = _make_transceiver(args.host, args.version, args.bmp_names)
    try:
        get_cores_in_run_state(transceiver, app_id, print_chips)
    finally:
        transceiver.close()


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
