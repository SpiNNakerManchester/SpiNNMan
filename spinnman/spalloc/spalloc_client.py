# Copyright (c) 2021 The University of Manchester
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
Implementation of the client for the Spalloc web service.
"""
import math
import os
import time
from logging import getLogger

import queue
import struct
import threading
from time import sleep
from typing import (Any, Callable, Dict, Final, FrozenSet, Iterable, List,
                    Mapping, Optional, Tuple, cast)
from urllib.parse import urlparse, urlunparse, ParseResult

from packaging.version import Version
import requests
from typing_extensions import TypeAlias
from websocket import WebSocket  # type: ignore

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinn_utilities.config_holder import (
    get_config_int, get_config_int_or_none, get_config_str_or_none)
from spinn_utilities.log import FormatAdapter
from spinn_utilities.typing.coords import XY
from spinn_utilities.typing.json import JsonObject, JsonValue
from spinn_utilities.overrides import overrides

from spinnman.connections.udp_packet_connections import UDPConnection
from spinnman.connections.abstract_classes import Connection, Listenable
from spinnman.constants import SCP_SCAMP_PORT, UDP_BOOT_CONNECTION_DEFAULT_PORT
from spinnman.data import SpiNNManDataView
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.exceptions import (
    SpallocBoardUnavailableException, SpallocException)
from spinnman.model.diagnostic_filter import DiagnosticFilter
from spinnman.transceiver import Transceiver

from .abstract_spalloc_client import AbstractSpallocClient
from .proxy_protocol import ProxyProtocol
from .session import Session, SessionAware
from .spalloc_boot_connection import SpallocBootConnection
from .spalloc_eieio_connection import SpallocEIEIOConnection
from .spalloc_eieio_listener import SpallocEIEIOListener
from .spalloc_job import SpallocJob
from .spalloc_machine import SpallocMachine
from .spalloc_proxied_connection import SpallocProxiedConnection
from .spalloc_scp_connection import SpallocSCPConnection
from .spalloc_state import SpallocState
from .utils import parse_service_url, get_hostname
from .spalloc_transceiver import SpallocTransceiver

logger = FormatAdapter(getLogger(__name__))
_open_req = struct.Struct("<IIIII")
_close_req = struct.Struct("<III")
_open_listen_req = struct.Struct("<II")
# Open and close share the response structure
_open_close_res = struct.Struct("<III")
_open_listen_res = struct.Struct("<IIIBBBBI")
_msg = struct.Struct("<II")
_msg_to = struct.Struct("<IIIII")

KEEP_ALIVE_PERIOND = 120

_WSCB: Final['TypeAlias'] = Callable[[Optional[bytes]], None]


def fix_url(url: Any) -> str:
    """
    Makes sure the url is the correct format.

    :param url: original url
    :returns: cleaned url
    """
    parts = urlparse(url)
    if parts.scheme != 'https':
        parts = ParseResult("https", parts.netloc, parts.path,
                            parts.params, parts. query, parts.fragment)
    if not parts.path.endswith("/"):
        parts = ParseResult(parts.scheme, parts.netloc, parts.path + "/",
                            parts.params, parts.query, parts.fragment)
    return urlunparse(parts)


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


class SpallocClient(AbstractContextManager, AbstractSpallocClient):
    """
    Basic client library for talking to new Spalloc.
    """
    __slots__ = ("__session",
                 "__machines_url", "__jobs_url", "version",
                 "__group", "__collab", "__nmpi_job", "__nmpi_user")

    def __init__(
            self, service_url: str,
            username: Optional[str] = None, password: Optional[str] = None,
            bearer_token: Optional[str] = None,
            group: Optional[str] = None, collab: Optional[str] = None,
            nmpi_job: Optional[int] = None, nmpi_user: Optional[str] = None):
        """
        :param service_url: The reference to the service.
            May have username and password supplied as part of the network
            location; if so, the ``username`` and ``password`` arguments
            *must* be ``None``. If ``username`` and ``password`` are not given,
            not even within the URL, the ``bearer_token`` must be not ``None``.
        :param username:
            The user name to use. If not provided nor in service_url
            environment variable SPALLOC_USER will be used.
        :param password:
            The password to use. If not provided nor in service_url
            environment variable SPALLOC_PASSWORD will be used.
        :param bearer_token: The bearer token to use
        """
        if username is None and password is None:
            service_url, username, password = parse_service_url(service_url)
        if username is None:
            username = os.getenv("SPALLOC_USER", None)
        if password is None:
            password = os.getenv("SPALLOC_PASSWORD", None)

        self.__session: Optional[Session] = Session(
            service_url, username, password, bearer_token)
        obj = self.__session.renew()
        v = cast(JsonObject, obj["version"])
        self.version = Version(
            f"{v['major-version']}.{v['minor-version']}.{v['revision']}")
        self.__machines_url = fix_url(obj["machines-ref"])
        self.__jobs_url = fix_url(obj["jobs-ref"])
        self.__group = group
        self.__collab = collab
        self.__nmpi_job = nmpi_job
        self.__nmpi_user = nmpi_user
        logger.info("established session to {} for {}", service_url, username)

    def get_job(self, job_id: str) -> SpallocJob:
        """
        Get a job by its job id.

        :param job_id: The job id.
        :returns: Job object for this ID
        """
        assert self.__session
        return _SpallocJob(
            self.__session, fix_url(f"{self.__jobs_url}/{job_id}"))

    @staticmethod
    def open_job_from_database(
            service_url: str, job_url: str, cookies: Dict[str, str],
            headers: Dict[str, str]) -> SpallocJob:
        """
        Create a job from the description in the attached database. This is
        intended to allow for access to the job's allocated resources from
        visualisers and other third party code participating in the SpiNNaker
        Tools Notification Protocol.

        .. note::
            The job is not verified to exist and be running. The session
            credentials may have expired; if so, the job will be unable to
            regenerate them.

        :param service_url:
        :param job_url:
        :param cookies:
        :param headers:

        :return:
            The job handle, or ``None`` if the records in the database are
            absent or incomplete.
        """
        session = Session(service_url, session_credentials=(cookies, headers))
        return _SpallocJob(session, job_url)

    @overrides(AbstractSpallocClient.list_machines)
    def list_machines(self) -> Dict[str, SpallocMachine]:
        assert self.__session
        obj = self.__session.get(self.__machines_url).json()
        return {m["name"]: _SpallocMachine(self.__session, m)
                for m in obj["machines"]}

    @overrides(AbstractSpallocClient.list_jobs)
    def list_jobs(self, deleted: bool = False) -> Iterable[SpallocJob]:
        assert self.__session
        obj = self.__session.get(
            self.__jobs_url,
            deleted=("true" if deleted else "false")).json()
        while obj["jobs"]:
            for u in obj["jobs"]:
                yield _SpallocJob(self.__session, fix_url(u))
            if "next" not in obj:
                break
            obj = self.__session.get(obj["next"]).json()

    @overrides(AbstractSpallocClient.create_job)
    def create_job(self) -> SpallocJob:
        assert self.__session

        operation: Dict[str, JsonValue] = {}

        spalloc_triad = get_config_str_or_none("Machine", "spalloc_triad")
        spalloc_physical = get_config_str_or_none(
            "Machine", "spalloc_physical")
        spalloc_ip_address = get_config_str_or_none(
            "Machine", "spalloc_ip_address")
        board_st: Optional[str] = None
        if spalloc_triad is not None:
            board_st = f"{spalloc_triad=}"
            triad = map(int, spalloc_triad.split(","))
            x, y, z = triad
            operation["board"] = {"x": int(x), "y": int(y), "z": int(z)}
        elif spalloc_physical is not None:
            board_st = f"{spalloc_physical=}"
            physical = map(int, spalloc_physical.split(","))
            c, f, b = physical
            operation["board"] = {
                "cabinet": int(c), "frame": int(f), "board": int(b)}
        elif spalloc_ip_address is not None:
            board_st = f"{spalloc_ip_address=}"
            operation["board"] = {"address": str(spalloc_ip_address)}

        spalloc_height = get_config_int_or_none("Machine", "spalloc_height")
        if spalloc_height is not None:
            spalloc_width = get_config_int("Machine", "spalloc_width")
            operation["dimensions"] = {
                "width": spalloc_width, "height": spalloc_height
            }
            if board_st is None:
                board_st = ""
            else:
                board_st += " "
            board_st += f"{spalloc_height=} {spalloc_width=}"
            logger.warning(f"Spalloc will return a fixed number of boards "
                           f"due to {board_st}")
        elif board_st is not None:
            logger.warning(f"Spalloc will return 1 board due to {board_st} "
                           f"and no spalloc_height and spalloc_width set")

        if not operation:
            n_boards = get_n_boards()
            logger.info(f"Requesting job with {n_boards} boards")
            operation["num-boards"] = n_boards

        machine_name = get_config_str_or_none("Machine", "spalloc_machine")
        if machine_name:
            operation["machine-name"] = machine_name
        else:
            operation["tags"] = ["default"]

        spalloc_max_dead_boards = get_config_int_or_none(
            "Machine", "spalloc_max_dead_boards")
        if spalloc_max_dead_boards is not None:
            operation["max-dead-boards"] = spalloc_max_dead_boards
            if board_st is not None:
                board_st += f" {spalloc_max_dead_boards=}"
            else:
                logger.warning(
                    f"{spalloc_max_dead_boards=} so spalloc may return a job "
                    "with less boards reachable than needed.")

        if self.__group is not None:
            operation["group"] = self.__group
        if self.__collab is not None:
            operation["nmpi-collab"] = self.__collab
        if self.__nmpi_job is not None:
            operation["nmpi-job-id"] = self.__nmpi_job
            if self.__nmpi_user is not None:
                operation["owner"] = self.__nmpi_user

        operation["keepalive-interval"] = f"PT{int(KEEP_ALIVE_PERIOND)}S"

        logger.info("requesting job with {}", operation)
        try:
            r = self.__session.post(self.__jobs_url, operation, timeout=30)
        except ValueError as exc:
            if board_st is not None:
                raise SpallocBoardUnavailableException(
                    f"Unable to allocated job with {board_st}") from exc
            raise
        url = r.headers["Location"]
        return _SpallocJob(self.__session, fix_url(url), board_st)

    def close(self) -> None:
        if self.__session is not None:
            self.__session.purge()
        self.__session = None


class _ProxyServiceError(IOError):
    """
    An error passed to us from the server over the proxy channel.
    """


class _SpallocMachine(SessionAware, SpallocMachine):
    """
    Represents a Spalloc-controlled machine.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ("__name", "__tags", "__width", "__height",
                 "__dead_boards", "__dead_links")

    def __init__(self, session: Session, machine_data: JsonObject):
        """
        :param session:
        :param machine_data:
        """
        super().__init__(session, cast(str, machine_data["uri"]))
        self.__name = cast(str, machine_data["name"])
        self.__tags = frozenset(cast(List[str], machine_data["tags"]))
        self.__width = cast(int, machine_data["width"])
        self.__height = cast(int, machine_data["height"])
        self.__dead_boards = cast(list, machine_data["dead-boards"])
        self.__dead_links = cast(list, machine_data["dead-links"])

    @property
    @overrides(SpallocMachine.name)
    def name(self) -> str:
        return self.__name

    @property
    @overrides(SpallocMachine.tags)
    def tags(self) -> FrozenSet[str]:
        return self.__tags

    @property
    @overrides(SpallocMachine.width)
    def width(self) -> int:
        return self.__width

    @property
    @overrides(SpallocMachine.height)
    def height(self) -> int:
        return self.__height

    @property
    @overrides(SpallocMachine.dead_boards)
    def dead_boards(self) -> list:
        return self.__dead_boards

    @property
    @overrides(SpallocMachine.dead_links)
    def dead_links(self) -> list:
        return self.__dead_links

    @property
    @overrides(SpallocMachine.area)
    def area(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def __repr__(self) -> str:
        return "SpallocMachine" + str((
            self.name, self.tags, self.width, self.height, self.dead_boards,
            self.dead_links))


class _ProxyPing(threading.Thread):
    """
    Sends ping messages to an open websocket
    """

    def __init__(self, websocket: WebSocket, sleep_time: int = 30):
        """
        :param websocket: WebSocket obtained when starting the client
        :param sleep_time: Time to wait between each ping sent
        """
        super().__init__(daemon=True)
        self.__ws = websocket
        self.__sleep_time = sleep_time
        self.__closed = False
        self.start()

    def run(self) -> None:
        """
        The handler loop of this thread
        """
        while self.__ws.connected:
            try:
                self.__ws.ping()
            except Exception:  # pylint: disable=broad-except
                # If closed, ignore error and get out of here
                if self.__closed:
                    break

                # Make someone aware of the error
                logger.exception("Error in websocket before close")
            sleep(self.__sleep_time)

    def close(self) -> None:
        """
        Mark as closed to avoid error messages.
        """
        self.__closed = True


class _ProxyReceiver(threading.Thread):
    """
    Receives all messages off an open websocket and dispatches them to
    registered listeners.
    """

    def __init__(self, websocket: WebSocket):
        """
        :param websocket: WebSocket obtained when starting the client
        """
        super().__init__(daemon=True)
        self.__ws = websocket
        self.__returns: Dict[int, _WSCB] = {}
        self.__handlers: Dict[int, _WSCB] = {}
        self.__correlation_id = 0
        self.__closed = False
        self.start()

    def run(self) -> None:
        """
        The handler loop of this thread.
        """
        while self.__ws.connected:
            try:
                result: Tuple[int, bytes] = self.__ws.recv_data()
                frame = result[1]
                if len(frame) < _msg.size:
                    # Message is out of protocol
                    continue
            except Exception:  # pylint: disable=broad-except
                # If closed, ignore error and get out of here
                if self.__closed:
                    break

                # Make someone aware of the error
                logger.exception("Error in websocket before close")

                # If we are disconnected before closing, make errors happen
                if not self.__ws.connected:
                    for rt in self.__returns.values():
                        rt(None)
                    for hd in self.__handlers.values():
                        hd(None)
                    break
            code, num = _msg.unpack_from(frame, 0)
            if code == ProxyProtocol.MSG:
                self.dispatch_message(num, frame)
            else:
                self.dispatch_return(num, frame)

    def expect_return(self, handler: _WSCB) -> int:
        """
        Register a one-shot listener for a call-like message's return.

        :return: The correlation ID
        """
        c = self.__correlation_id
        self.__correlation_id += 1
        self.__returns[c] = handler
        return c

    def listen(self, channel_id: int, handler: _WSCB) -> None:
        """
        Register a persistent listener for one-way messages.
        """
        self.__handlers[channel_id] = handler

    def dispatch_return(self, correlation_id: int, msg: bytes) -> None:
        """
        Dispatch a received call-return message.
        """
        handler = self.__returns.pop(correlation_id, None)
        if handler:
            handler(msg)

    def dispatch_message(self, channel_id: int, msg: bytes) -> None:
        """
        Dispatch a received one-way message.
        """
        handler = self.__handlers.get(channel_id)
        if handler:
            handler(msg)

    def unlisten(self, channel_id: int) -> None:
        """
        Deregister a listener for a channel
        """
        self.__handlers.pop(channel_id)

    def close(self) -> None:
        """
        Mark receiver closed to avoid errors
        """
        self.__closed = True


class _SpallocJob(SessionAware, SpallocJob):
    """
    Represents a job in Spalloc.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ("__board_st", "__machine_url", "__chip_url",
                 "__memory_url", "__router_url",
                 "_keepalive_url", "__proxy_handle",
                 "__proxy_thread", "__proxy_ping")

    def __init__(self, session: Session, job_handle: str,
                 board_st: Optional[str] = None):
        """
        :param session: The session created when starting the spalloc client
        :param job_handle: url
        :param board_st: Name and Value of cfg setting for specific board
        """
        super().__init__(session, job_handle)
        logger.info("established job at {}", job_handle)
        self.__board_st = board_st
        self.__machine_url = self._url + "machine"
        self.__chip_url = self._url + "chip"
        self.__memory_url = self._url + "memory"
        self.__router_url = self._url + "router"
        self._keepalive_url: Optional[str] = self._url + "keepalive"
        self.__proxy_handle: Optional[WebSocket] = None
        self.__proxy_thread: Optional[_ProxyReceiver] = None
        self.__proxy_ping: Optional[_ProxyPing] = None
        keep_alive = threading.Thread(
            target=self.__start_keepalive, daemon=True)
        keep_alive.start()

    @overrides(SpallocJob.get_session_credentials_for_db)
    def get_session_credentials_for_db(self) -> Mapping[Tuple[str, str], str]:
        config = {}
        config["SPALLOC", "service uri"] = self._service_url
        config["SPALLOC", "job uri"] = self._url
        cookies, headers = self._session_credentials
        if "Authorization" in headers:
            # We never write the authorisation headers themselves;
            # we just extend the session
            del headers["Authorization"]
        for k, v in cookies.items():
            config["COOKIE", k] = v
        for k, v in headers.items():
            config["HEADER", k] = v
        return config

    @overrides(SpallocJob.get_state)
    def get_state(self, wait_for_change: bool = False) -> SpallocState:
        timeout: Optional[int] = 10
        if wait_for_change:
            timeout = None
        obj = self._get(
            self._url, wait=wait_for_change, timeout=timeout).json()
        return SpallocState[obj["state"]]

    @overrides(SpallocJob.get_root_host)
    def get_root_host(self) -> Optional[str]:
        r = self._get(self.__machine_url)
        if r.status_code == 204:
            return None
        obj = r.json()
        for c in obj["connections"]:
            [x, y], host = c
            if x == 0 and y == 0:
                return host
        return None

    @overrides(SpallocJob.get_connections)
    def get_connections(self) -> Dict[XY, str]:
        r = self._get(self.__machine_url)
        if r.status_code == 204:
            return {}
        return {
            (int(x), int(y)): str(host)
            for ((x, y), host) in r.json()["connections"]
        }

    @property
    def __proxy_url(self) -> Optional[str]:
        """
        The URL for talking to the proxy connection system.
        """
        r = self._get(self._url)
        if r.status_code == 204:
            return None
        try:
            url = r.json()["proxy-ref"]
            logger.info("Connecting to proxy on {}", url)
            return url
        except KeyError:
            return None

    def __init_proxy(self) -> Tuple[_ProxyReceiver, WebSocket]:
        if self.__proxy_handle is None or not self.__proxy_handle.connected:
            if self.__proxy_url is None:
                raise ValueError("no proxy available")
            self.__proxy_handle = self._websocket(
                self.__proxy_url, origin=get_hostname(self._url))
            self.__proxy_thread = _ProxyReceiver(self.__proxy_handle)
            self.__proxy_ping = _ProxyPing(self.__proxy_handle)
        assert self.__proxy_handle is not None
        assert self.__proxy_thread is not None
        return self.__proxy_thread, self.__proxy_handle

    @overrides(SpallocJob.connect_to_board)
    def connect_to_board(
            self, x: int, y: int,
            port: int = SCP_SCAMP_PORT) -> SpallocSCPConnection:
        proxy, ws = self.__init_proxy()
        return _ProxiedSCAMPConnection(ws, proxy, int(x), int(y), int(port))

    @overrides(SpallocJob.connect_for_booting)
    def connect_for_booting(self) -> SpallocBootConnection:
        proxy, ws = self.__init_proxy()
        return _ProxiedBootConnection(ws, proxy)

    @overrides(SpallocJob.open_eieio_connection)
    def open_eieio_connection(self, x: int, y: int) -> SpallocEIEIOConnection:
        proxy, ws = self.__init_proxy()
        return _ProxiedEIEIOConnection(
            ws, proxy, int(x), int(y), SCP_SCAMP_PORT)

    @overrides(SpallocJob.open_eieio_listener_connection)
    def open_eieio_listener_connection(self) -> SpallocEIEIOListener:
        proxy, ws = self.__init_proxy()
        return _ProxiedEIEIOListener(ws, proxy, self.get_connections())

    @overrides(SpallocJob.open_udp_listener_connection)
    def open_udp_listener_connection(self) -> UDPConnection:
        proxy, ws = self.__init_proxy()
        return _ProxiedUDPListener(ws, proxy, self.get_connections())

    @overrides(SpallocJob.wait_for_state_change)
    def wait_for_state_change(self, old_state: SpallocState,
                              timeout: Optional[int] = None) -> SpallocState:
        while old_state != SpallocState.DESTROYED:
            obj = self._get(self._url, wait="true", timeout=timeout).json()
            s = SpallocState[obj["state"]]
            if s != old_state or s == SpallocState.DESTROYED:
                return s
        return old_state

    @overrides(SpallocJob.wait_until_ready)
    def wait_until_ready(self) -> None:
        n_retries = 3
        state = self.get_state()
        retries = 0

        while state == SpallocState.QUEUED:
            logger.info(f"Waiting as job is QUEUED {retries=}")
            if self.__board_st is not None:
                if retries >= n_retries:
                    raise SpallocBoardUnavailableException(
                        f"Boards described as {self.__board_st} "
                        f"are not available")
            time.sleep(5)
            retries += 1
            state = self.get_state()

        while state == SpallocState.POWER:
            logger.info(f"Waiting as job is powering up {retries=}")
            time.sleep(5)
            retries += 1
            state = self.get_state()

        if state != SpallocState.READY:
            raise SpallocException(f"job was unexpectedly {state=}")

    @overrides(SpallocJob.destroy)
    def destroy(self, reason: str = "finished") -> None:
        self._keepalive_url = None
        if self.__proxy_handle is not None:
            if self.__proxy_thread:
                self.__proxy_thread.close()
            if self.__proxy_ping:
                self.__proxy_ping.close()
            self.__proxy_handle.close()
        self._delete(self._url, reason=str(reason))
        logger.info("deleted job at {}", self._url)

    @overrides(SpallocJob.write_data)
    def write_data(self, x: int, y: int, address: int, data: bytes) -> None:
        self._post_raw(self.__memory_url, data=data, x=x, y=y, address=address)

    @overrides(SpallocJob.read_data)
    def read_data(self, x: int, y: int, address: int, size: int) -> bytes:
        response = self._get(self.__memory_url, x=x, y=y, address=address,
                             size=size)
        return response.content

    @overrides(SpallocJob.reset_routing)
    def reset_routing(
            self, custom_filters: Dict[int, DiagnosticFilter]) -> None:
        keys = {str(i): f.filter_word for i, f in custom_filters.items()}
        self._delete(self.__router_url, **keys)

    def __keepalive(self) -> bool:
        """
        Signal spalloc that we want the job to stay alive for a while longer.

        :return: False if the job has not been destroyed
        """
        if self._keepalive_url is None:
            return False
        cookies, headers = self._session_credentials
        headers["Content-Type"] = "text/plain; charset=UTF-8"
        logger.debug(self._keepalive_url)
        requests.put(self._keepalive_url, data="alive", cookies=cookies,
                     headers=headers, allow_redirects=False, timeout=10)
        return True

    def __start_keepalive(self) -> None:
        """
        Method for keep alive thread to start the keep alive class

        """
        try:
            while self.__keepalive():
                time.sleep(KEEP_ALIVE_PERIOND / 2)
        except Exception as ex:  # pylint: disable=broad-except
            logger.exception(ex)

    @overrides(SpallocJob.where_is_machine)
    def where_is_machine(self, x: int, y: int) -> Optional[
            Tuple[int, int, int]]:
        r = self._get(self.__chip_url, x=int(x), y=int(y))
        if r.status_code == 204:
            return None
        return cast(Tuple[int, int, int], tuple(
            r.json()["physical-board-coordinates"]))

    @overrides(SpallocJob.create_transceiver)
    def create_transceiver(
            self, ensure_board_is_ready: bool = True) -> Transceiver:
        if self.get_state() != SpallocState.READY:
            raise SpallocException("job not ready to execute scripts")
        return SpallocTransceiver(
            self, ensure_board_is_ready=ensure_board_is_ready)

    def __repr__(self) -> str:
        return f"SpallocJob({self._url})"


class _ProxiedConnection(metaclass=AbstractBase):
    """
    Core multiplexer/demultiplexer emulating a connection that is proxied
    over a websocket.

    None of the methods are public because subclasses may expose a profile of
    them to conform to a particular type of connection.
    """

    def __init__(self, websocket: WebSocket, receiver: _ProxyReceiver):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        """
        self.__ws: Optional[WebSocket] = websocket
        self.__receiver: Optional[_ProxyReceiver] = receiver
        self.__msgs: queue.SimpleQueue = queue.SimpleQueue()
        self.__call_queue: queue.Queue = queue.Queue(1)
        self.__call_lock = threading.RLock()
        self.__current_msg: Optional[bytes] = None
        self.__handle = self._open_connection()
        self.__receiver.listen(self.__handle, self.__msgs.put)

    @abstractmethod
    def _open_connection(self) -> int:
        raise NotImplementedError

    def _call(self, protocol: ProxyProtocol, packer: struct.Struct,
              unpacker: struct.Struct, *args: int) -> Tuple[Any, ...]:
        """
        Do a synchronous call.

        :param protocol:
            The protocol message number.
        :param packer:
            How to form the protocol message. The first two arguments passed
            will be the protocol message number and an issued correlation ID
            (not needed by the caller).
        :param unpacker:
            How to extract the expected response.
        :param args:
            Additional arguments to pass to the packer.
        :return:
            The results from the unpacker *after* the protocol message code and
            the correlation ID.
        :raises IOError:
            If something goes wrong. This could be due to the websocket being
            closed, or the receipt of an ERROR response.
        """
        if not self._connected:
            raise IOError("socket closed")
        if not self.__receiver:
            raise IOError("socket closed")
        if not self.__ws:
            raise IOError("socket closed")
        with self.__call_lock:
            # All calls via websocket use correlation_id
            correlation_id = self.__receiver.expect_return(
                self.__call_queue.put)
            self.__ws.send_binary(packer.pack(protocol, correlation_id, *args))
            if not self._connected:
                raise IOError("socket closed after send!")
            reply = self.__call_queue.get()
            code, _ = _msg.unpack_from(reply, 0)
            if code == ProxyProtocol.ERROR:
                # Rest of message is UTF-8 encoded error message string
                payload = reply[_msg.size:].decode("utf-8")
                if len(payload):
                    raise _ProxyServiceError(payload)
                raise _ProxyServiceError(
                    f"unknown problem with {protocol} call")
            return unpacker.unpack(reply)[2:]

    @property
    def _connected(self) -> bool:
        return bool(self.__ws and self.__ws.connected)

    def _throw_if_closed(self) -> None:
        if not self._connected:
            raise IOError("socket closed")

    def _close(self) -> None:
        if self._connected:
            channel_id, = self._call(
                ProxyProtocol.CLOSE, _close_req, _open_close_res,
                self.__handle)
            if channel_id != self.__handle:
                raise IOError("failed to close proxy socket")
        if self.__receiver:
            self.__receiver.unlisten(self.__handle)
        self.__ws = None
        self.__receiver = None

    def _send(self, message: bytes) -> None:
        self._throw_if_closed()
        # Put the header on the front and send it
        if not self.__ws:
            raise IOError("socket closed")
        self.__ws.send_binary(_msg.pack(
            ProxyProtocol.MSG, self.__handle) + message)

    def _send_to(self, message: bytes, x: int, y: int, port: int) -> None:
        self._throw_if_closed()
        # Put the header on the front and send it
        if not self.__ws:
            raise IOError("socket closed")
        self.__ws.send_binary(_msg_to.pack(
            ProxyProtocol.MSG_TO, self.__handle, x, y, port) + message)

    def __get(self, timeout: float = 0.5) -> bytes:
        """
        Get a value from the queue. Handles block/non-block switching and
        trimming of the message protocol prefix.
        """
        if not timeout:
            return self.__msgs.get(block=False)[_msg.size:]
        else:
            return self.__msgs.get(timeout=timeout)[_msg.size:]

    def _receive(self, timeout: Optional[float] = None) -> bytes:
        if self.__current_msg is not None:
            try:
                return self.__current_msg
            finally:
                self.__current_msg = None
        if timeout is None:
            while True:
                try:
                    return self.__get()
                except queue.Empty:
                    self._throw_if_closed()
        else:
            try:
                return self.__get(timeout)
            except queue.Empty as e:
                self._throw_if_closed()
                raise SpinnmanTimeoutException("receive", timeout) from e

    def _is_ready_to_receive(self, timeout: float = 0) -> bool:
        # If we already have a message or the queue peek succeeds, return now
        if self.__current_msg is not None or not self.__msgs.empty():
            return True
        try:
            self.__current_msg = self.__get(timeout)
            return True
        except queue.Empty:
            return False


class _ProxiedBidirectionalConnection(
        _ProxiedConnection, SpallocProxiedConnection):
    """
    A connection that talks to a particular board via the proxy.
    """

    def __init__(
            self, websocket: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        :param x: X coordinate of the board's Ethernet-enabled chip
        :param y: Y coordinate of the board's Ethernet-enabled chip
        :param port: UDP port to talk to; defaults to the SCP port
        """
        self.__connect_args = (x, y, port)
        super().__init__(websocket, receiver)

    @overrides(_ProxiedConnection._open_connection)
    def _open_connection(self) -> int:
        handle, = self._call(
            ProxyProtocol.OPEN, _open_req, _open_close_res,
            *self.__connect_args)
        return handle

    @overrides(Connection.is_connected)
    def is_connected(self) -> bool:
        """
        Determines if the medium is connected at this point in time.

        :return: True if the medium is connected, False otherwise
        """
        return self._connected

    @overrides(Connection.close)
    def close(self) -> None:
        """
        Closes the connection.
        """
        self._close()

    @overrides(SpallocProxiedConnection.send)
    def send(self, data: bytes) -> None:
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data)
        self._send(data)

    @overrides(SpallocProxiedConnection.receive)
    def receive(self, timeout: Optional[float] = None) -> bytes:
        return self._receive(timeout)

    @overrides(Listenable.is_ready_to_receive)
    def is_ready_to_receive(self, timeout: float = 0) -> bool:
        return self._is_ready_to_receive(timeout)

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class _ProxiedUnboundConnection(
        _ProxiedConnection, SpallocProxiedConnection):
    """
    A connection that can listen to all boards via the proxy, but which can
    only send if a target board is provided.
    """

    def __init__(self, websocket: WebSocket, receiver: _ProxyReceiver):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        """
        super().__init__(websocket, receiver)
        self.__addr: Optional[str] = None
        self.__port: Optional[int] = None

    @overrides(_ProxiedConnection._open_connection)
    def _open_connection(self) -> int:
        handle, ip1, ip2, ip3, ip4, self.__port = self._call(
            ProxyProtocol.OPEN_UNBOUND, _open_listen_req, _open_listen_res)
        # Assemble the address into the format expected elsewhere
        self.__addr = f"{ip1}.{ip2}.{ip3}.{ip4}"
        return handle

    @property
    def _addr(self) -> Optional[str]:
        return self.__addr if self._connected else None

    @property
    def _port(self) -> Optional[int]:
        return self.__port if self._connected else None

    @overrides(Connection.is_connected)
    def is_connected(self) -> bool:
        """
        Determines if the medium is connected at this point in time.

        :return: True if the medium is connected, False otherwise
        """
        return self._connected

    @overrides(Connection.close)
    def close(self) -> None:
        """
        Closes the connection.
        """
        self._close()

    @overrides(SpallocProxiedConnection.send)
    def send(self, data: bytes) -> None:
        self._throw_if_closed()
        raise IOError("socket is not open for sending")

    @overrides(SpallocProxiedConnection.receive)
    def receive(self, timeout: Optional[float] = None) -> bytes:
        return self._receive(timeout)

    @overrides(Listenable.is_ready_to_receive)
    def is_ready_to_receive(self, timeout: float = 0) -> bool:
        return self._is_ready_to_receive(timeout)

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class _ProxiedSCAMPConnection(
        _ProxiedBidirectionalConnection, SpallocSCPConnection):
    __slots__ = ("__chip_x", "__chip_y")

    def __init__(
            self, websocket: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        :param x: X coordinate of the board's Ethernet-enabled chip
        :param y: Y coordinate of the board's Ethernet-enabled chip
        :param port: UDP port to talk to; defaults to the SCP port
        """
        super().__init__(websocket, receiver, x, y, port)
        SpallocSCPConnection.__init__(self, x, y)

    def __str__(self) -> str:
        return f"SCAMPConnection[proxied]({self.chip_x},{self.chip_y})"


class _ProxiedBootConnection(
        _ProxiedBidirectionalConnection, SpallocBootConnection):
    __slots__ = ()

    def __init__(self, websocket: WebSocket, receiver: _ProxyReceiver):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        """
        _ProxiedBidirectionalConnection.__init__(
            self, websocket, receiver, 0, 0, UDP_BOOT_CONNECTION_DEFAULT_PORT)
        SpallocBootConnection.__init__(self)

    def __str__(self) -> str:
        return "BootConnection[proxied]()"


class _ProxiedEIEIOConnection(
        _ProxiedBidirectionalConnection,
        SpallocEIEIOConnection):
    # Special: This is a unidirectional receive-only connection
    __slots__ = ("__addr", "__port", "__chip_x", "__chip_y")

    def __init__(
            self, websocket: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        :param x: X coordinate of the board's Ethernet-enabled chip
        :param y: Y coordinate of the board's Ethernet-enabled chip
        :param port: UDP port to talk to; defaults to the SCP port
        """
        _ProxiedBidirectionalConnection.__init__(
            self, websocket, receiver, x, y, port)
        SpallocEIEIOConnection.__init__(self)
        self.__chip_x = x
        self.__chip_y = y

    @property
    @overrides(SpallocEIEIOConnection._coords)
    def _coords(self) -> XY:
        return self.__chip_x, self.__chip_y

    @overrides(SpallocEIEIOConnection.send_to)
    def send_to(self, data: bytes, address: tuple) -> None:
        """
        Direct ``send_to`` is unsupported.
        """
        _ = (data, address)
        self._throw_if_closed()
        raise IOError("socket is not open for sending")

    def __str__(self) -> str:
        return (f"EIEIOConnection[proxied](remote:{self.__chip_x},"
                f"{self.__chip_y})")


class _ProxiedEIEIOListener(_ProxiedUnboundConnection, SpallocEIEIOListener):
    __slots__ = ("__conns", )

    def __init__(self, websocket: WebSocket, receiver: _ProxyReceiver,
                 connections: Dict[XY, str]):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        :param connections:
           Get the mapping from board coordinates to IP addresses.
        """
        _ProxiedUnboundConnection.__init__(self, websocket, receiver)
        SpallocEIEIOListener.__init__(self)
        # Invert the map
        self.__conns = {ip: xy for (xy, ip) in connections.items()}

    @overrides(SpallocEIEIOListener.send_to_chip)
    def send_to_chip(self, message: bytes, x: int, y: int,
                     port: int = SCP_SCAMP_PORT) -> None:
        if not isinstance(message, (bytes, bytearray)):
            message = bytes(message)
        self._send_to(bytes(message), x, y, port)

    @property
    @overrides(SpallocEIEIOListener.local_ip_address)
    def local_ip_address(self) -> str:
        return self._addr or "0.0.0.0"

    @property
    @overrides(SpallocEIEIOListener.local_port)
    def local_port(self) -> int:
        return self._port or 0

    @overrides(SpallocEIEIOListener._get_chip_coords)
    def _get_chip_coords(self, ip_address: str) -> XY:
        return self.__conns[str(ip_address)]

    def __str__(self) -> str:
        return f"EIEIOConnection[proxied](local:{self._addr}:{self._port})"


class _ProxiedUDPListener(_ProxiedUnboundConnection, UDPConnection):
    __slots__ = ("__conns", )

    def __init__(self, websocket: WebSocket, receiver: _ProxyReceiver,
                 connections: Dict[XY, str]):
        """
        :param websocket: WebSocket obtained when starting the client
        :param receiver: Receiver created when starting the Client
        :param connections:
           Get the mapping from board coordinates to IP addresses.
        """
        _ProxiedUnboundConnection.__init__(self, websocket, receiver)
        UDPConnection.__init__(self)
        # Invert the map
        self.__conns = {ip: xy for (xy, ip) in connections.items()}

    @overrides(UDPConnection.send_to)
    def send_to(self, data: bytes, address: Tuple[str, int]) -> None:
        ip, port = address
        x, y = self.__conns[ip]
        self._send_to(data, x, y, port)

    @property
    @overrides(UDPConnection.local_ip_address)
    def local_ip_address(self) -> str:
        return self._addr or "0.0.0.0"

    @property
    @overrides(UDPConnection.local_port)
    def local_port(self) -> int:
        return self._port or 0

    def __str__(self) -> str:
        return f"UDPConnection[proxied](local:{self._addr}:{self._port})"
