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
from functools import partial
import logging
from types import TracebackType
from typing import Dict, Set
from spinn_utilities.log import FormatAdapter
from spinn_machine import Chip, CoreSubsets
from spinnman.data import SpiNNManDataView
from spinnman.messages.scp.impl import AppCopyRun, CheckOKResponse
from spinnman.connections.udp_packet_connections import SCAMPConnection
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
logger = FormatAdapter(logging.getLogger(__name__))


class ApplicationCopyRunProcess(
        AbstractMultiConnectionProcess[CheckOKResponse]):
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
    __slots__ = ("__chips_done", "__blacklisted_links")

    def __get_next_chips(self) -> Dict[Chip, int]:
        """
        Get the chips that are adjacent to the last set of chips, which
        haven't yet been loaded.  Also returned are the links for each chip,
        which gives the link which should be read from to get the data.

        :return: An dictionary from *target* chips to the link to copy *from*.
        :rtype: iterable(dict(Chip, int))
        """
        next_chips: Dict[Chip, int] = dict()
        for chip in self.__chips_done:
            for link in chip.router.links:
                next_chip = SpiNNManDataView.get_chip_at(
                    link.destination_x, link.destination_y)
                if next_chip not in self.__chips_done and (
                        next_chip not in next_chips):
                    # Get the opposite of the link direction
                    next_link = (link.source_link_id + 3) % 6
                    if next_chip not in self.__blacklisted_links or (
                            next_link not in self.__blacklisted_links[
                                next_chip]):
                        next_chips[next_chip] = next_link
                        # Only let one thing copy from this chip
                        break
        return next_chips

    def run(self, size: int, app_id: int, core_subsets: CoreSubsets,
            chksum: int, wait: bool):
        """
        Run the process.

        :param int size: The size of the binary to copy
        :param int app_id: The application id to assign to the running binary
        :param CoreSubsets core_subsets: The cores to load the binary on to
        :param int chksum: The checksum of the data to test against
        :param bool wait:
            Whether to put the binary in "wait" mode or run it straight away
        """
        # pylint: disable=attribute-defined-outside-init
        boot_chip = SpiNNManDataView.get_machine().boot_chip
        self.__chips_done: Dict[Chip, int] = dict()
        self.__blacklisted_links: Dict[Chip, Set[int]] = defaultdict(set)
        # We use a dict to get reliable iteration order; values unimportant
        self.__chips_done[boot_chip] = 0

        while (next_chips := self.__get_next_chips()):
            # Do all the chips at the current level
            with self._collect_responses():
                for chip, link in next_chips.items():
                    subset = core_subsets.get_core_subset_for_chip(
                        chip.x, chip.y)
                    self._send_request(AppCopyRun(
                        chip.x, chip.y, link, size, app_id,
                        subset.processor_ids, chksum, wait),
                        partial(self.__chip_done, chip),
                        partial(self.__chip_err, chip, link))

    def __chip_done(self, chip: Chip):
        """
        Mark the chip as done, and thus eligible to be a source for copying
        from.
        """
        self.__chips_done[chip] = 1

    def __chip_err(
            self, chip: Chip, link: int, request: AppCopyRun,
            exception: Exception, tb: TracebackType,
            connection: SCAMPConnection):
        """
        This link not working? Blacklist it (for this process, not generally).
        Pass through to the standard error handler if the chip isn't reachable
        in a reliable fashion at all (i.e., all links into the chip are
        exhausted).
        """
        self.__blacklisted_links[chip].add(link)
        logger.debug("chip {},{} link {} failed due to {}",
                     chip.x, chip.y, link, str(exception))
        # pylint: disable=protected-access
        if len(self.__blacklisted_links[chip]) == len(chip.router._links):
            self._receive_error(request, exception, tb, connection)
