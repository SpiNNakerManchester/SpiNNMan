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


def _get_next_chips(old_next_chips, machine, chips_done):
    next_chips = set()
    for _old_link, chip in old_next_chips:
        for link in chip.router.links:
            chip_coords = (link.destination_x, link.destination_y)
            if chip_coords not in chips_done:
                opp_link = (link.source_link_id + 3) % 6
                next_chips.add((opp_link, machine.get_chip_at(*chip_coords)))
    return next_chips


class ApplicationCopyRunProcess(AbstractMultiConnectionProcess):
    __slots__ = []

    def run(self, machine, size, app_id, core_subsets, wait):
        boot_chip = machine.boot_chip
        chips_done = set((boot_chip.x, boot_chip.y))
        next_chips = _get_next_chips([(None, boot_chip)], machine, chips_done)

        while next_chips:
            # Do all the chips at the current level
            for link, chip in next_chips:
                subset = core_subsets.get_core_subset_for_chip(chip.x, chip.y)
                self._send_request(AppCopyRun(
                    chip.x, chip.y, link, size, app_id, subset.processor_ids,
                    wait))
                chips_done.add((chip.x, chip.y))
            self._finish()
            self.check_for_error()
            next_chips = _get_next_chips(next_chips, machine, chips_done)
