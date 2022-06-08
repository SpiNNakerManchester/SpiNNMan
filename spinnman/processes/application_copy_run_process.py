# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinnman.messages.scp.impl import AppCopyRun
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


def _on_same_board(chip_1, chip_2):
    return (chip_1.nearest_ethernet_x == chip_2.nearest_ethernet_x and
            chip_1.nearest_ethernet_y == chip_2.nearest_ethernet_y)


def _board_already_copied_to(chip, boards_copied_to):
    board_addr = (chip.nearest_ethernet_x, chip.nearest_ethernet_y)
    return board_addr in boards_copied_to


def _do_copy(chip_from, chip_to, boards_copied_to):
    # Never copy to a virtual chip
    if chip_to.is_virtual:
        return False
    # We can always copy if on the same board
    if _on_same_board(chip_from, chip_to):
        return True
    # If not on the same board, but the board has already been copied to,
    # don't copy to that board again (as that causes timeouts)
    if _board_already_copied_to(chip_to, boards_copied_to):
        return False
    # If we haven't copied to this board, do the copy this once, but then stop
    # it happening again
    boards_copied_to.add(
        (chip_to.nearest_ethernet_x, chip_to.nearest_ethernet_y))
    return True


def _get_next_chips(old_next_chips, machine, chips_done, boards_copied_to):
    """ Get the chips that are adjacent to the last set of chips, which
        haven't yet been loaded.  Also returned are the links for each chip,
        which gives the link which should be read from to get the data.

    :param list(int,Chip) old_next_chips:
        The chips to find the chips adjacent to
    :param Machine machine: The machine containing the chips
    :param set(int,int) The coordinates of chips that have already been done
    :return: A dict of chip coordinates to link to use, Chip
    :rtype: dict((int,int), (int, Chip))
    """
    next_chips = dict()
    for _old_link, chip in old_next_chips.values():
        for link in chip.router.links:
            chip_coords = (link.destination_x, link.destination_y)
            if chip_coords not in chips_done and chip_coords not in next_chips:
                next_chip = machine.get_chip_at(*chip_coords)
                if _do_copy(chip, next_chip, boards_copied_to):
                    opp_link = (link.source_link_id + 3) % 6
                    next_chips[chip_coords] = (opp_link, next_chip)
    return next_chips


class ApplicationCopyRunProcess(AbstractMultiConnectionProcess):
    """ Process to start a binary on a subset of cores on a subset of chips
        of a machine, performed by, on each chip, copying the data from
        an adjacent chip and then starting the binary.  This goes to each
        chip in turn, and so detects failures early on, as well as ensuring
        that the copy and execution is done in the case of success i.e. this
        ensures that if all commands are successful, the full binary has been
        copied and started.

        NOTE: The binary must have been loaded to the boot chip before this is
        called!
    """
    __slots__ = []

    def run(self, machine, size, app_id, core_subsets, wait):
        """ Run the process.

        :param Machine machine: The machine to run the process on
        :param int size: The size of the binary to copy
        :param int app_id: The application id to assign to the running binary
        :param CoreSubsets core_subsets: The cores to load the binary on to
        :param bool wait:
            Whether to put the binary in "wait" mode or run it straight away
        """
        boot_chip = machine.boot_chip
        chips_done = set([(boot_chip.x, boot_chip.y)])
        boards_copied_to = set(chips_done)
        next_chips = {(boot_chip.x, boot_chip.y): (None, boot_chip)}
        next_chips = _get_next_chips(
            next_chips, machine, chips_done, boards_copied_to)

        while next_chips:
            # Do all the chips at the current level
            for link, chip in next_chips.values():
                subset = core_subsets.get_core_subset_for_chip(chip.x, chip.y)
                self._send_request(AppCopyRun(
                    chip.x, chip.y, link, size, app_id, subset.processor_ids,
                    wait))
                chips_done.add((chip.x, chip.y))
            self._finish()
            self.check_for_error()
            next_chips = _get_next_chips(
                next_chips, machine, chips_done, boards_copied_to)
