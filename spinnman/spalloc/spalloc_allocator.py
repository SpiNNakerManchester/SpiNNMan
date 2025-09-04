# Copyright (c) 2016 The University of Manchester
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

from contextlib import ExitStack
import logging
import math
from typing import cast, ContextManager, Dict, Tuple, Optional, Union

from spinn_utilities.config_holder import (
    get_config_bool, get_config_str_or_none)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY
from spinn_utilities.config_holder import get_config_str

from spinnman.connections.udp_packet_connections import (
    SCAMPConnection, EIEIOConnection)
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.data import SpiNNManDataView
from spinnman.spalloc import (
    MachineAllocationController,
    SpallocClient, SpallocJob, SpallocState)
from spinnman.transceiver import Transceiver


logger = FormatAdapter(logging.getLogger(__name__))


class SpallocJobController(MachineAllocationController):
    """
    A class to Create and support Transceivers specific for Spalloc.
    """

    __slots__ = (
        # the spalloc job object
        "_job",
        # the current job's old state
        "_state",
        "__client",
        "__use_proxy"
    )

    def __init__(
            self, client: SpallocClient, job: SpallocJob, use_proxy: bool):
        if job is None:
            raise TypeError("must have a real job")
        self.__client = client
        self._job = job
        self._state = job.get_state()
        self.__use_proxy = use_proxy
        super().__init__("SpallocJobController")

    @property
    def job(self) -> SpallocJob:
        """
        The job value passed into the init.
        """
        return self._job

    @overrides(MachineAllocationController.extend_allocation)
    def extend_allocation(self, new_total_run_time: float) -> None:
        # Does Nothing in this allocator - machines are held until exit
        pass

    def __stop(self) -> None:
        self._job.destroy()
        self.__client.close()

    @overrides(MachineAllocationController.close)
    def close(self) -> None:
        super().close()
        self.__stop()

    @overrides(MachineAllocationController.where_is_machine)
    def where_is_machine(
            self, chip_x: int, chip_y: int) -> Tuple[int, int, int]:
        result = self._job.where_is_machine(x=chip_x, y=chip_y)
        if result is None:
            raise ValueError("coordinates lie outside machine")
        return result

    @overrides(MachineAllocationController._wait)
    def _wait(self) -> bool:
        try:
            if self._state != SpallocState.DESTROYED:
                self._state = self._job.wait_for_state_change(self._state)
        except TypeError:
            pass
        except Exception as e:  # pylint: disable=broad-except
            if not self._exited:
                raise e
        return self._state != SpallocState.DESTROYED

    @overrides(MachineAllocationController._teardown)
    def _teardown(self) -> None:
        if not self._exited:
            self.__stop()
        super()._teardown()

    @overrides(MachineAllocationController.create_transceiver,
               extend_doc=True)
    def create_transceiver(self) -> Transceiver:
        """
        .. note::
            This allocation controller proxies the transceiver's connections
            via Spalloc. This allows it to work even outside the UNIMAN
            firewall.
        """
        if not self.__use_proxy:
            return super().create_transceiver()
        txrx = self._job.create_transceiver()
        return txrx

    @overrides(MachineAllocationController.can_create_transceiver)
    def can_create_transceiver(self) -> bool:
        if not self.__use_proxy:
            return super().can_create_transceiver()
        return True

    @overrides(MachineAllocationController.open_sdp_connection,
               extend_doc=True)
    def open_sdp_connection(
            self, chip_x: int, chip_y: int,
            udp_port: int = SCP_SCAMP_PORT) -> Optional[SCAMPConnection]:
        """
        .. note::
            This allocation controller proxies connections via Spalloc. This
            allows it to work even outside the UNIMAN firewall.
        """
        if not self.__use_proxy:
            return super().open_sdp_connection(chip_x, chip_y, udp_port)
        return self._job.connect_to_board(chip_x, chip_y, udp_port)

    @overrides(MachineAllocationController.open_eieio_connection,
               extend_doc=True)
    def open_eieio_connection(
            self, chip_x: int, chip_y: int) -> Optional[EIEIOConnection]:
        """
        .. note::
            This allocation controller proxies connections via Spalloc. This
            allows it to work even outside the UNIMAN firewall.
        """
        if not self.__use_proxy:
            return super().open_eieio_connection(chip_x, chip_y)
        return self._job.open_eieio_connection(chip_x, chip_y)

    @overrides(MachineAllocationController.open_eieio_listener,
               extend_doc=True)
    def open_eieio_listener(self) -> EIEIOConnection:
        """
        .. note::
            This allocation controller proxies connections via Spalloc. This
            allows it to work even outside the UNIMAN firewall.
        """
        if not self.__use_proxy:
            return super().open_eieio_listener()
        return self._job.open_eieio_listener_connection()

    @property
    @overrides(MachineAllocationController.proxying)
    def proxying(self) -> bool:
        return self.__use_proxy

    def __str__(self) -> str:
        return f"SpallocJobController over {self._job}"


def get_n_boards() -> int:
    """
    Works out how many boards are needed.

    :return: Number of boards needed with a safety factor
    :raises ~spinn_utilities.exceptions.SpiNNUtilsException:
        If data needed is not available
    """
    if SpiNNManDataView.has_n_boards_required():
        return SpiNNManDataView.get_n_boards_required()
    else:
        n_chips = SpiNNManDataView.get_n_chips_needed()
        # reduce max chips by 2 in case you get a bad board(s)
        chips_div = (
                SpiNNManDataView.get_machine_version().n_chips_per_board - 2)
        n_boards_float = float(n_chips) / chips_div
        logger.info("{:.2f} Boards Required for {} chips",
                    n_boards_float, n_chips)
        # If the number of boards rounded up is less than 50% of a board
        # bigger than the actual number of boards,
        # add another board just in case.
        n_boards = int(math.ceil(n_boards_float))
        if n_boards - n_boards_float < 0.5:
            n_boards += 1
        return n_boards


def spalloc_allocate_job(
        bearer_token: Optional[str] = None, group: Optional[str] = None,
        collab: Optional[str] = None, nmpi_job: Union[int, str, None] = None,
        nmpi_user: Optional[str] = None) -> Tuple[
            str, int, Dict[XY, str], MachineAllocationController]:
    """
    Request a machine from an new-style spalloc server that will fit the
    given number of boards.

    :param bearer_token: The bearer token to use
    :param group: The group to associate with or None for no group
    :param collab: The collab to associate with or None for no collab
    :param nmpi_job: The NMPI Job to associate with or None for no job
    :param nmpi_user: The NMPI username to associate with or None for no user
    """
    spalloc_server = get_config_str("Machine", "spalloc_server")
    n_boards = get_n_boards()
    logger.info(f"Requesting job with {n_boards} boards")
    with ExitStack() as stack:
        spalloc_machine = get_config_str_or_none("Machine", "spalloc_machine")
        use_proxy = get_config_bool("Machine", "spalloc_use_proxy")
        if nmpi_job is None:
            _nmpi_job: Optional[int] = None
        else:
            _nmpi_job = int(nmpi_job)
        client = SpallocClient(
            spalloc_server, bearer_token=bearer_token, group=group,
            collab=collab, nmpi_job=_nmpi_job, nmpi_user=nmpi_user)
        stack.enter_context(cast(ContextManager[SpallocClient], client))
        job = client.create_job(n_boards, spalloc_machine)
        stack.enter_context(job)
        job.wait_until_ready()
        connections = job.get_connections()
        root = connections.get((0, 0), None)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "boards: {}",
                str(connections).replace("{", "[").replace("}", "]"))
        allocation_controller = SpallocJobController(
            client, job, use_proxy or False)
        # Success! We don't want to close the client, job or task now;
        # the allocation controller now owns them.
        stack.pop_all()
    assert root is not None, "no root of ready board"
    version = 5
    return (root, version, connections, allocation_controller)
