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
import logging
from types import TracebackType
from typing import Callable, Dict, List, Set
from spinn_utilities.log import FormatAdapter
from spinn_machine import Chip, CoreSubsets
from spinnman.data import SpiNNManDataView
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl import AppCopyRun, CheckOKResponse
from spinnman.connections.udp_packet_connections import SCAMPConnection
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.exceptions import SpinnmanException
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
    __slots__ = (
        "__chips_done", "__blacklisted_links", "__advanced", "__round_errors")
    # pylint: disable=attribute-defined-outside-init

    def __get_next_chips(self, core_subsets: CoreSubsets) -> Dict[Chip, int]:
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
        if not next_chips and not self.__advanced and (
                len(core_subsets) != len(self.__chips_done)):
            missing = []
            for subset in core_subsets.core_subsets:
                chip = SpiNNManDataView.get_chip_at(subset.x, subset.y)
                if chip not in self.__chips_done:
                    missing.append((subset.x, subset.y))
            if missing:
                raise SpinnmanException(
                    f"Could not fill to all chips: {missing = }")
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
        boot_chip = SpiNNManDataView.get_machine().boot_chip
        self.__chips_done: Dict[Chip, int] = dict()
        self.__blacklisted_links: Dict[Chip, Set[int]] = defaultdict(set)
        # We use a dict to get reliable iteration order; values unimportant
        self.__chips_done[boot_chip] = 0
        self.__advanced: bool = False

        while (next_chips := self.__get_next_chips(core_subsets)):
            self.__advanced = False
            self.__round_errors: List[SpinnmanException] = []
            # Do all the chips at the current level
            with self._collect_responses():
                for chip, link in next_chips.items():
                    subset = core_subsets.get_core_subset_for_chip(
                        chip.x, chip.y)
                    self._send_request(AppCopyRun(
                        chip.x, chip.y, link, size, app_id,
                        subset.processor_ids, chksum, wait),
                        self.__on_chip_done(chip),
                        self.__on_chip_err(chip, link))
            if not self.__advanced:
                logger.warning(
                    "round of copies could not reach {}", next_chips.keys())
                for ex in self.__round_errors:
                    logger.warning("failure:", exc_info=ex)

    def __on_chip_done(self, chip: Chip) -> Callable[[CheckOKResponse], None]:
        """
        Generate a response handler to mark the chip as done, and thus eligible
        to be a source for copying from.
        """
        def handler(_r: CheckOKResponse) -> None:
            self.__chips_done[chip] = 1
            self.__advanced = True

        return handler

    def __on_chip_err(self, chip: Chip, link: int) -> Callable[
            [AbstractSCPRequest, Exception, TracebackType, SCAMPConnection],
            None]:
        """
        This link not working? The callback this generates will blacklist it
        (for this process, not generally), and will pass through to the
        standard error handler if the chip isn't reachable in a reliable
        fashion at all (i.e., all links into the chip are exhausted) or the
        failure is not of an expected class.
        """
        def handler(
                request: AbstractSCPRequest, exception: Exception,
                tb: TracebackType, connection: SCAMPConnection):
            if isinstance(exception, SpinnmanException):
                logger.warning("chip {},{} link {} failed due to {}",
                               chip.x, chip.y, link, str(exception))
                self.__round_errors.append(exception)
                if not self.__blacklist_link(chip, link):
                    return
            self._receive_error(request, exception, tb, connection)

        return handler

    def __blacklist_link(self, chip: Chip, link: int) -> bool:
        """
        How to blacklist a link.

        :param chip: The target chip
        :param link: The inbound link to the target chip that failed
        :return: True if we know a chip is definitely unreachable.
        """
        self.__blacklisted_links[chip].add(link)
        # pylint: disable=protected-access
        return len(self.__blacklisted_links[chip]) == len(chip.router._links)
