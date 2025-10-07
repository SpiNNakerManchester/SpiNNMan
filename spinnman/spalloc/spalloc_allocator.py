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
import os
import re
from typing import cast, ContextManager, Dict, Tuple, Optional, Union

import ebrains_drive  # type: ignore[import]
import requests

from spinn_utilities.config_holder import (
    get_config_bool, get_config_str_or_none)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XY
from spinn_utilities.config_holder import get_config_str

from spinnman.connections.udp_packet_connections import SCAMPConnection
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.spalloc import (
    MachineAllocationController,
    SpallocClient, SpallocJob, SpallocState)
from spinnman.transceiver import Transceiver


logger = FormatAdapter(logging.getLogger(__name__))

SHARED_PATH = re.compile(r".*\/shared\/([^\/]+)")
SHARED_GROUP = 1
SHARED_WITH_PATH = re.compile(r".*\/Shared with (all|groups|me)\/([^\/]+)")
SHARED_WITH_GROUP = 2


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
        """
        :param client:
        :param job:
        :param use_proxy:
        """
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

    def create_transceiver(self, ensure_board_is_ready: bool) -> Transceiver:
        """
        Create a Transceiver using proxy

        .. note::
            This allocation controller proxies the transceiver's connections
            via Spalloc. This allows it to work even outside the UNIMAN
            firewall.

        :param ensure_board_is_ready:
            Flag to say if ensure_board_is_ready should be run
        :returns: A proxied Transceiver
        """
        if self.__use_proxy:
            return self._job.create_transceiver(ensure_board_is_ready)
        raise NotImplementedError(
            "create transceiver only supported if using proxy")

    def can_create_transceiver(self) -> bool:
        """
        :returns: True if create_transceiver would work
        """
        return self.__use_proxy

    def open_sdp_connection(
            self, chip_x: int, chip_y: int,
            udp_port: int = SCP_SCAMP_PORT) -> Optional[SCAMPConnection]:
        """
        Open a connection to a specific Ethernet-enabled SpiNNaker chip.
        Caller will have to arrange for SpiNNaker to pay attention to the
        connection.
        The coordinates will be job-relative.
        .. note::
            This allocation controller proxies connections via Spalloc. This
            allows it to work even outside the UNIMAN firewall.

        :param chip_x: Ethernet-enabled chip X coordinate
        :param chip_y: Ethernet-enabled chip Y coordinate
        :param udp_port:
            the UDP port on the chip to connect to; connecting to a non-SCP
            port will result in a connection that can't easily be configured.
        :returns:
           Connection to the Chip with a know host over this port or None
        """
        if self.__use_proxy:
            return self._job.connect_to_board(chip_x, chip_y, udp_port)
        else:
            return None

    @property
    @overrides(MachineAllocationController.proxying)
    def proxying(self) -> bool:
        return self.__use_proxy

    def __str__(self) -> str:
        return f"SpallocJobController over {self._job}"


def __bearer_token() -> Optional[str]:
    """
    :return: The OIDC bearer token
    """
    # Try using Jupyter if we have the right variables
    jupyter_token = os.getenv("JUPYTERHUB_API_TOKEN")
    jupyter_ip = os.getenv("JUPYTERHUB_SERVICE_HOST")
    jupyter_port = os.getenv("JUPYTERHUB_SERVICE_PORT")
    if (jupyter_token is not None and jupyter_ip is not None and
            jupyter_port is not None):
        jupyter_url = (f"http://{jupyter_ip}:{jupyter_port}/services/"
                       "access-token-service/access-token")
        headers = {"Authorization": f"Token {jupyter_token}"}
        response = requests.get(jupyter_url, headers=headers, timeout=10)
        return response.json().get('access_token')

    # Try a simple environment variable, or None if that doesn't exist
    return os.getenv("OIDC_BEARER_TOKEN")


def __get_collab_id_from_folder(folder: str) -> Optional[Dict[str, str]]:
    """
    Currently hacky way to get the EBRAINS collab id from the
    drive folder, replicated from the NMPI collab template.
    """
    token = __bearer_token
    if token is None:
        return None
    ebrains_drive_client = ebrains_drive.connect(token=token)
    repo_by_title = ebrains_drive_client.repos.get_repos_by_name(folder)
    if len(repo_by_title) != 1:
        logger.warning(f"The repository for collab {folder} could not be"
                       " found; continuing as if not in a collaboratory")
        return {}
    # Owner is formatted as collab-<collab_id>-<permission>, and we want
    # to extract the <collab-id>
    owner = repo_by_title[0].owner
    collab_id = owner[:owner.rindex("-")]
    collab_id = collab_id[collab_id.find("-") + 1:]
    logger.info(f"Requesting job in collaboratory {collab_id}")
    return {"collab": collab_id}


def __group_collab_or_job() -> Dict[str, str]:
    """
    :return: The group, collab, or NMPI Job ID to associate with jobs
    """
    # Try to get a NMPI Job
    nmpi_job = os.getenv("NMPI_JOB_ID")
    if nmpi_job is not None and nmpi_job != "":
        nmpi_user = os.getenv("NMPI_USER")
        if nmpi_user is not None and nmpi_user != "":
            logger.info("Requesting job for NMPI job {}, user {}",
                        nmpi_job, nmpi_user)
            return {"nmpi_job": nmpi_job, "nmpi_user": nmpi_user}
        logger.info("Requesting spalloc job for NMPI job {}", nmpi_job)
        return {"nmpi_job": nmpi_job}

    # Try to get the collab from the path
    cwd = os.getcwd()
    match_obj = SHARED_PATH.match(cwd)
    if match_obj:
        collab = __get_collab_id_from_folder(
            match_obj.group(SHARED_GROUP))
        if collab is not None:
            return collab
    match_obj = SHARED_WITH_PATH.match(cwd)
    if match_obj:
        collab = __get_collab_id_from_folder(
            match_obj.group(SHARED_WITH_GROUP))
        if collab is not None:
            return collab

    # Try to use the config to get a group
    group = get_config_str_or_none("Machine", "spalloc_group")
    if group is not None:
        return {"group": group}

    # Nothing ventured, nothing gained
    return {}


def spalloc_allocate_job() -> Tuple[
            str, Dict[XY, str], SpallocJobController]:
    """
    Request a machine from an new-style spalloc server that will fit the
    given number of boards.

    :return: host, board address map, allocation controller
    """
    return __spalloc_allocate_job(
        __bearer_token(), **__group_collab_or_job())


def __spalloc_allocate_job(
        bearer_token: Optional[str] = None, group: Optional[str] = None,
        collab: Optional[str] = None, nmpi_job: Union[int, str, None] = None,
        nmpi_user: Optional[str] = None) -> Tuple[
            str, Dict[XY, str], SpallocJobController]:
    """
    Request a machine from an new-style spalloc server that will fit the
    given number of boards.

    :param bearer_token: The bearer token to use
    :param group: The group to associate with or None for no group
    :param collab: The collab to associate with or None for no collab
    :param nmpi_job: The NMPI Job to associate with or None for no job
    :param nmpi_user: The NMPI username to associate with or None for no user
    :return: host, board address map, allocation controller

    """
    spalloc_server = get_config_str("Machine", "spalloc_server")
    with ExitStack() as stack:
        use_proxy = get_config_bool("Machine", "spalloc_use_proxy")
        if nmpi_job is None:
            _nmpi_job: Optional[int] = None
        else:
            _nmpi_job = int(nmpi_job)
        client = SpallocClient(
            spalloc_server, bearer_token=bearer_token, group=group,
            collab=collab, nmpi_job=_nmpi_job, nmpi_user=nmpi_user)
        stack.enter_context(cast(ContextManager[SpallocClient], client))
        job = client.create_job()
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
    return (root, connections, allocation_controller)
