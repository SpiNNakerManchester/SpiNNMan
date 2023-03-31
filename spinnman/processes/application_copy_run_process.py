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

from spinnman.data import SpiNNManDataView
from spinnman.messages.scp.impl import AppCopyRun
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


def _on_same_board(chip_1, chip_2):
    return (chip_1.nearest_ethernet_x == chip_2.nearest_ethernet_x and
            chip_1.nearest_ethernet_y == chip_2.nearest_ethernet_y)


def _get_next_chips(chips_done):
    """
    Get the chips that are adjacent to the last set of chips, which
    haven't yet been loaded.  Also returned are the links for each chip,
    which gives the link which should be read from to get the data.

    :param set((int,int)) chips_done:
        The coordinates of chips that have already been done
    :return: A dict of chip coordinates to link to use, Chip
    :rtype: dict((int,int), (int, Chip))
    """
    next_chips = dict()
    for x, y in chips_done:
        chip = SpiNNManDataView.get_chip_at(x, y)
        for link in chip.router.links:
            chip_coords = (link.destination_x, link.destination_y)
            if chip_coords not in chips_done and chip_coords not in next_chips:
                next_chip = SpiNNManDataView.get_chip_at(*chip_coords)
                opp_link = (link.source_link_id + 3) % 6
                next_chips[chip_coords] = (opp_link, next_chip)
                # Only let one thing copy from this chip
                break
    return next_chips


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
    __slots__ = []

    def run(self, size, app_id, core_subsets, chksum, wait):
        """
        Run the process.

        :param int size: The size of the binary to copy
        :param int app_id: The application id to assign to the running binary
        :param CoreSubsets core_subsets: The cores to load the binary on to
        :param int chksum: The checksum of the data to test against
        :param bool wait:
            Whether to put the binary in "wait" mode or run it straight away
        """
        boot_chip = SpiNNManDataView.get_machine().boot_chip
        chips_done = set([(boot_chip.x, boot_chip.y)])
        next_chips = _get_next_chips(chips_done)

        while next_chips:
            # Do all the chips at the current level
            for link, chip in next_chips.values():
                subset = core_subsets.get_core_subset_for_chip(chip.x, chip.y)
                self._send_request(AppCopyRun(
                    chip.x, chip.y, link, size, app_id, subset.processor_ids,
                    chksum, wait))
                chips_done.add((chip.x, chip.y))
            self._finish()
            self.check_for_error()
            next_chips = _get_next_chips(chips_done)
