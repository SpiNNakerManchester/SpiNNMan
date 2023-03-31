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

import os.path
import time
import logging
from spinn_utilities.log import FormatAdapter

logger = FormatAdapter(logging.getLogger(__name__))
_REPORT_NAME = "machine_structure.rpt"


def generate_machine_report(report_directory, machine, connections):
    """
    Generate report on the physical structure of the target SpiNNaker machine.

    :param str report_directory: the directory to which reports are stored
    :param ~spinn_machine.Machine machine: the machine python object
    :param list(Connection) connections:
        the list of connections to the machine
    :raise IOError: when a file cannot be opened for some reason
    """
    file_name = os.path.join(report_directory, _REPORT_NAME)
    time_date_string = time.strftime("%c")
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            _write_header(f, time_date_string, machine, connections)
            # TODO: Add further details on the target machine.
            for chip in machine.chips:
                _write_chip_router_report(f, chip)
    except IOError:
        logger.exception(
            "Generate_placement_reports: Can't open file {} for writing.",
            file_name)
        raise


def _write_header(f, timestamp, machine, connections):
    """
    :param str timestamp:
    :param ~spinn_machine.Machine machine:
    :param list(Connection) connections:
    """
    f.write("\t\tTarget SpiNNaker Machine Structure\n")
    f.write("\t\t==================================\n")
    f.write(f"\nGenerated: {timestamp} for target machine '{connections}'\n\n")
    f.write(f"Machine dimensions (in chips) x : {machine.width}  "
            f"y : {machine.height}\n\n")
    f.write("\t\tMachine router information\n")
    f.write("\t\t==========================\n")


def _write_chip_router_report(f, chip):
    """
    :param ~spinn_machine.Chip chip:
    """
    f.write(f"\nInformation for chip {chip.x}:{chip.y}\n")
    f.write("Neighbouring chips\n"
            f"{chip.router.get_neighbouring_chips_coords()}\n")
    f.write("Router list of links for this chip are: \n")
    for link in chip.router.links:
        f.write(f"\t{link}\n")
    f.write("\t\t==========================\n")
