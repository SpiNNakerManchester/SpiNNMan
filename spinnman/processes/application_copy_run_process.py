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

from collections import defaultdict
from typing import cast, Iterable, List, Mapping, Tuple
from spinn_machine import Chip, CoreSubsets, Link, Machine
from spinnman.data import SpiNNManDataView
from spinnman.messages.scp.impl import AppCopyRun
from spinnman.processes import ConnectionSelector
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

APP_COPY_RUN_TIMEOUT = 6.0


def _on_same_board(chip_1: Chip, chip_2: Chip) -> bool:
    return (chip_1.nearest_ethernet_x == chip_2.nearest_ethernet_x and
            chip_1.nearest_ethernet_y == chip_2.nearest_ethernet_y)


def _get_next_chips(
        chips_done: Mapping[Tuple[int, int], List[Tuple[int, int]]],
        parent_chips: Mapping[Tuple[int, int], List[Chip]],
        machine: Machine) -> Iterable[Chip]:
    """
    Get the chips that are adjacent to the last set of chips, which
    haven't yet been loaded.  Also returned are the links for each chip,
    which gives the link which should be read from to get the data.

    :param chips_done:
        The coordinates of chips that have already been done by Ethernet
    :param parent_chips:
        A dictionary of chip coordinates to chips that use that chip as a
        parent
    :return: A list of next chips to use
    """
    next_chips: List[Chip] = list()
    for eth_chip in chips_done:
        off_board_copy_done = False
        for c_x, c_y in chips_done[eth_chip]:
            chip_xy = machine[c_x, c_y]
            for chip in parent_chips[c_x, c_y]:
                on_same_board = _on_same_board(chip, chip_xy)
                eth = (chip.nearest_ethernet_x, chip.nearest_ethernet_y)
                if (eth not in chips_done or
                        chip not in chips_done[eth]):
                    if on_same_board or not off_board_copy_done:
                        next_chips.append(chip)
                        if not on_same_board:
                            off_board_copy_done = True
                        # Only do one copy from each chip at a time
                        break

    return next_chips


def _compute_parent_chips(
        machine: Machine) -> Mapping[Tuple[int, int], List[Chip]]:
    """
    Compute a dictionary of chip coordinates to list of chips who use that chip
    as a parent in the tree.

    :param machine: The machine to compute the map for
    """
    chip_links: Mapping[Tuple[int, int], List[Chip]] = defaultdict(list)
    for chip in machine.chips:
        if chip.parent_link is not None:
            link = cast(Link, chip.router.get_link(chip.parent_link))
            chip_links[link.destination_x, link.destination_y].append(chip)
    return chip_links


class ApplicationCopyRunProcess(AbstractMultiConnectionProcess):
    """
    Process to start a binary on a subset of cores on a subset of chips
    of a machine, performed by, on each chip, copying the data from
    an adjacent chip and then starting the binary.  This goes to each
    chip in turn, and so detects failures early on, as well as ensuring
    that the copy and execution is done in the case of success i.e. this
    ensures that if all commands are successful, the full binary has been
    copied and started.

    .. note::
        The binary must have been loaded to the boot chip before this is
        called!
    """
    __slots__ = ()

    def __init__(self, next_connection_selector: ConnectionSelector,
                 timeout: float = APP_COPY_RUN_TIMEOUT):
        """
        :param next_connection_selector:
           Method to find the next connection to use
        :param timeout:
           How long to wait for a response before raising an Exception
        """
        AbstractMultiConnectionProcess.__init__(
            self, next_connection_selector, timeout=timeout)

    def run(self, size: int, app_id: int, core_subsets: CoreSubsets,
            checksum: int, wait: bool) -> None:
        """
        Run the process.

        :param size: The size of the binary to copy
        :param app_id: The application id to assign to the running binary
        :param core_subsets: The cores to load the binary on to
        :param checksum: The checksum of the data to test against
        :param wait:
            Whether to put the binary in "wait" mode or run it straight away
        """
        machine = SpiNNManDataView.get_machine()
        boot_chip = machine.boot_chip
        chips_done: Mapping[Tuple[int, int], List[Tuple[int, int]]] = \
            defaultdict(list)
        chips_done[boot_chip].append((boot_chip))
        parent_chips = _compute_parent_chips(machine)
        next_chips = _get_next_chips(chips_done, parent_chips, machine)

        while next_chips:
            # Do all the chips at the current level
            for chip in next_chips:
                subset = core_subsets.get_core_subset_for_chip(chip.x, chip.y)
                self._send_request(AppCopyRun(
                    chip.x, chip.y, cast(int, chip.parent_link), size, app_id,
                    subset.processor_ids, checksum, wait))
                eth = (chip.nearest_ethernet_x, chip.nearest_ethernet_y)
                chips_done[eth].append(chip)
            self._finish()
            self.check_for_error()
            next_chips = _get_next_chips(chips_done, parent_chips, machine)
