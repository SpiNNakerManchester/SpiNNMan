# Copyright (c) 2021-2022 The University of Manchester
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
"""
Implementation of the client for the Spalloc web service.
"""

from logging import getLogger
from multiprocessing import Process, Queue
from packaging.version import Version
import queue
import requests
import sqlite3
import struct
import threading
from typing import Dict, List, Tuple
from websocket import WebSocket
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import (
    Connection, Listenable, SCPSender)
from spinnman.constants import SCP_SCAMP_PORT, UDP_BOOT_CONNECTION_DEFAULT_PORT
from spinnman.exceptions import SpinnmanTimeoutException
from .enums import SpallocState, ProxyProtocol
from .session import Session, SessionAware
from .utils import parse_service_url, get_hostname
from .abstract_classes import (
    AbstractSpallocClient, SpallocProxiedConnectionBase,
    SpallocProxiedConnection, SpallocBootConnection, SpallocJob,
    SpallocMachine, SpallocEIEIOConnection, SpallocEIEIOListener)
from spinnman.transceiver import Transceiver

logger = FormatAdapter(getLogger(__name__))
_open_req = struct.Struct("<IIIII")
_close_req = struct.Struct("<III")
_open_listen_req = struct.Struct("<II")
# Open and close share the response structure
_open_close_res = struct.Struct("<III")
_open_listen_res = struct.Struct("<IIB4I")
_msg = struct.Struct("<II")
_msg_to = struct.Struct("<IIII")


class SpallocClient(AbstractContextManager, AbstractSpallocClient):
    """
    Basic client library for talking to new Spalloc.
    """
    __slots__ = ("__session",
                 "__machines_url", "__jobs_url", "version")

    def __init__(
            self, service_url, username=None, password=None,
            bearer_token=None):
        """
        :param str service_url: The reference to the service.
            May have username and password supplied as part of the network
            location; if so, the ``username`` and ``password`` arguments
            *must* be ``None``. If ``username`` and ``password`` are not given,
            not even within the URL, the ``bearer_token`` must be not ``None``.
        :param str username: The user name to use
        :param str password: The password to use
        :param str bearer_token: The bearer token to use
        """
        if username is None and password is None:
            service_url, username, password = parse_service_url(service_url)
        self.__session = Session(service_url, username, password, bearer_token)
        if not bearer_token:
            obj = self.__session.renew()
        v = obj["version"]
        self.version = Version(
            f"{v['major-version']}.{v['minor-version']}.{v['revision']}")
        self.__machines_url = obj["machines-ref"]
        self.__jobs_url = obj["jobs-ref"]
        logger.info("established session to {} for {}", service_url, username)

    @staticmethod
    def open_job_from_database(conn: sqlite3.Cursor) -> SpallocJob:
        """
        Create a job from the description in the attached database. This is
        intended to allow for access to the job's allocated resources from
        visualisers and other third party code participating in the Spinnaker
        Tools Notification Protocol.

        .. note ::

            The job is not verified to exist and be running. The session
            credentials may have expired; if so, the job will be unable to
            regenerate them.

        :param ~sqlite3.Cursor conn:
            The database cursor to retrieve the job details from. Assumes
            the presence of a ``proxy_configuration`` table with ``kind``,
            ``name`` and ``value`` columns.
        :return:
            The job handle, or ``None`` if the records in the database are
            absent or incomplete.
        :rtype: SpallocJob
        """
        service_url = None
        job_url = None
        cookies = {}
        headers = {}
        for row in conn.execute(
                """ SELECT kind, name, value FROM proxy_configuration"""):
            kind, name, value = row
            if kind == "SPALLOC":
                if name == "service uri":
                    service_url = value
                elif name == "job uri":
                    job_url = value
            elif kind == "COOKIE":
                cookies[name] = value
            elif kind == "HEADER":
                headers[name] = value
        if not service_url or not job_url or not cookies or not headers:
            # Cannot possibly work without a session or job
            return None
        session = Session(service_url, session_credentials=(cookies, headers))
        return _SpallocJob(session, job_url)

    @overrides(AbstractSpallocClient.list_machines)
    def list_machines(self):
        obj = self.__session.get(self.__machines_url).json()
        return {m["name"]: _SpallocMachine(self, m) for m in obj["machines"]}

    @overrides(AbstractSpallocClient.list_jobs)
    def list_jobs(self, deleted=False):
        obj = self.__session.get(
            self.__jobs_url,
            deleted=("true" if deleted else "false")).json()
        while obj["jobs"]:
            for u in obj["jobs"]:
                yield _SpallocJob(self.__session, u)
            if "next" not in obj:
                break
            obj = self.__session.get(obj["next"]).json()

    def _create(self, create, machine_name):
        if machine_name:
            create["machine-name"] = machine_name
        else:
            create["tags"] = ["default"]
        r = self.__session.post(self.__jobs_url, create)
        url = r.headers["Location"]
        return _SpallocJob(self.__session, url)

    @overrides(AbstractSpallocClient.create_job)
    def create_job(self, num_boards=1, machine_name=None, keepalive=45):
        return self._create({
            "num-boards": int(num_boards),
            "keepalive-interval": f"PT{int(keepalive)}S"
        }, machine_name)

    @overrides(AbstractSpallocClient.create_job_rect)
    def create_job_rect(self, width, height, machine_name=None, keepalive=45):
        return self._create({
            "dimensions": {
                "width": int(width),
                "height": int(height)
            },
            "keepalive-interval": f"PT{int(keepalive)}S"
        }, machine_name)

    @overrides(AbstractSpallocClient.create_job_board)
    def create_job_board(
            self, triad=None, physical=None, ip_address=None,
            machine_name=None, keepalive=45):
        if triad:
            x, y, z = triad
            board = {"x": x, "y": y, "z": z}
        elif physical:
            c, f, b = physical
            board = {"cabinet": c, "frame": f, "board": b}
        elif ip_address:
            board = {"address": str(ip_address)}
        else:
            raise KeyError("at least one of triad, physical and ip_address "
                           "must be given")
        return self._create({
            "board": board,
            "keepalive-interval": f"PT{int(keepalive)}S"
        }, machine_name)

    def close(self):
        if self.__session is not None:
            self.__session._purge()
        self.__session = None


def _SpallocKeepalive(url, interval, term_queue, cookies, headers):
    """
    Actual keepalive task implementation. Don't use directly.
    """
    headers["Content-Type"] = "text/plain; charset=UTF-8"
    while True:
        requests.put(url, data="alive", cookies=cookies, headers=headers,
                     allow_redirects=False)
        try:
            term_queue.get(True, interval)
            break
        except queue.Empty:
            continue


class _SpallocMachine(SessionAware, SpallocMachine):
    """
    Represents a spalloc-controlled machine.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ("__name", "__tags", "__width", "__height",
                 "__dead_boards", "__dead_links")

    def __init__(self, session, machine_data):
        """
        :param _Session session:
        :param dict machine_data:
        """
        super().__init__(session, machine_data["uri"])
        self.__name = machine_data["name"]
        self.__tags = frozenset(machine_data["tags"])
        self.__width = machine_data["width"]
        self.__height = machine_data["height"]
        self.__dead_boards = machine_data["dead-boards"]
        self.__dead_links = machine_data["dead-links"]

    @property
    @overrides(SpallocMachine.name)
    def name(self):
        return self.__name

    @property
    @overrides(SpallocMachine.tags)
    def tags(self):
        return self.__tags

    @property
    @overrides(SpallocMachine.width)
    def width(self):
        return self.__width

    @property
    @overrides(SpallocMachine.height)
    def height(self):
        return self.__height

    @property
    @overrides(SpallocMachine.dead_boards)
    def dead_boards(self):
        return self.__dead_boards

    @property
    @overrides(SpallocMachine.dead_links)
    def dead_links(self):
        return self.__dead_links

    @property
    @overrides(SpallocMachine.area)
    def area(self):
        return (self.width, self.height)

    def __repr__(self):
        return "SpallocMachine" + str((
            self.name, self.tags, self.width, self.height, self.dead_boards,
            self.dead_links))


class _ProxyReceiver(threading.Thread):
    """
    Receives all messages off an open websocket and dispatches them to
    registered listeners.
    """

    def __init__(self, ws):
        super().__init__(daemon=True)
        self.__ws = ws
        self.__returns = {}
        self.__handlers = {}
        self.__correlation_id = 0
        self.start()

    def run(self):
        """
        The handler loop of this thread.
        """
        while self.__ws.connected:
            try:
                result = self.__ws.recv_data()
                frame = result[1]
                if len(frame) < _msg.size:
                    # Message is out of protocol
                    continue
            except Exception:  # pylint: disable=broad-except
                break
            code, num = _msg.unpack_from(frame, 0)
            if code == ProxyProtocol.MSG:
                self.dispatch_message(num, frame)
            else:
                self.dispatch_return(num, frame)

    def expect_return(self, handler) -> int:
        """
        Register a one-shot listener for a call-like message's return.

        :return: The correlation ID
        """
        c = self.__correlation_id
        self.__correlation_id += 1
        self.__returns[c] = handler
        return c

    def listen(self, channel_id: int, handler):
        """
        Register a persistent listener for one-way messages.
        """
        self.__handlers[channel_id] = handler

    def dispatch_return(self, correlation_id: int, msg: bytes):
        """
        Dispatch a received call-return message.
        """
        handler = self.__returns.pop(correlation_id, None)
        if handler:
            handler(msg)

    def dispatch_message(self, channel_id: int, msg: bytes):
        """
        Dispatch a received one-way message.
        """
        handler = self.__handlers.get(channel_id, None)
        if handler:
            handler(msg)


class _SpallocJob(SessionAware, SpallocJob):
    """
    Represents a job in spalloc.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ("__machine_url", "__chip_url",
                 "_keepalive_url", "__keepalive_handle", "__proxy_handle",
                 "__proxy_thread")

    def __init__(self, session, job_handle):
        """
        :param _Session session:
        :param str job_handle:
        """
        super().__init__(session, job_handle)
        logger.info("established job at {}", job_handle)
        self.__machine_url = self._url + "machine"
        self.__chip_url = self._url + "chip"
        self._keepalive_url = self._url + "keepalive"
        self.__keepalive_handle = None
        self.__proxy_handle = None
        self.__proxy_thread = None

    @overrides(SpallocJob._write_session_credentials_to_db)
    def _write_session_credentials_to_db(self, cur):
        config = {}
        config["SPALLOC", "service uri"] = self._service_url
        config["SPALLOC", "job uri"] = self._url
        cookies, headers = self._session_credentials()
        for k, v in cookies.items():
            config["COOKIE", k] = v
        for k, v in headers.items():
            config["HEADER", k] = v
        if "Authorization" in headers:
            # We never write the auth headers themselves; we just extend the
            # session
            del headers["Authorization"]
        cur.executemany("""
            INSERT INTO proxy_configuration(kind, name, value)
            VALUES(?, ?, ?)
            """, [(k1, k2, v) for (k1, k2), v in config.items()])

    @overrides(SpallocJob.get_state)
    def get_state(self):
        obj = self._get(self._url).json()
        return SpallocState[obj["state"]]

    @overrides(SpallocJob.get_root_host)
    def get_root_host(self):
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
    def get_connections(self):
        r = self._get(self.__machine_url)
        if r.status_code == 204:
            return None
        return {
            (int(x), int(y)): str(host)
            for ((x, y), host) in r.json()["connections"]
        }

    @property
    def __proxy_url(self):
        """
        Get the URL for talking to the proxy connection system.
        """
        r = self._get(self._url)
        if r.status_code == 204:
            return None
        try:
            return r.json()["proxy-ref"]
        except KeyError:
            return None

    def __init_proxy(self):
        if self.__proxy_handle is None or not self.__proxy_handle.connected:
            self.__proxy_handle = self._websocket(
                self.__proxy_url, origin=get_hostname(self._url))
            self.__proxy_thread = _ProxyReceiver(self.__proxy_handle)

    @overrides(SpallocJob.connect_to_board)
    def connect_to_board(self, x, y, port=SCP_SCAMP_PORT):
        self.__init_proxy()
        return _ProxiedSCAMPConnection(
            self.__proxy_handle, self.__proxy_thread, x, y, port)

    @overrides(SpallocJob.connect_for_booting)
    def connect_for_booting(self):
        self.__init_proxy()
        return _ProxiedBootConnection(self.__proxy_handle, self.__proxy_thread)

    @overrides(SpallocJob.open_eieio_connection)
    def open_eieio_connection(self, x, y):
        self.__init_proxy()
        return _ProxiedEIEIOConnection(
            self.__proxy_handle, self.__proxy_thread, x, y, SCP_SCAMP_PORT)

    @overrides(SpallocJob.open_listener_connection)
    def open_listener_connection(self):
        self.__init_proxy()
        return _ProxiedEIEIOListener(
            self.__proxy_handle, self.__proxy_thread, self.get_connections())

    @overrides(SpallocJob.wait_for_state_change)
    def wait_for_state_change(self, old_state):
        while old_state != SpallocState.DESTROYED:
            obj = self._get(self._url, wait="true").json()
            s = SpallocState[obj["state"]]
            if s != old_state or s == SpallocState.DESTROYED:
                return s
        return old_state

    @overrides(SpallocJob.wait_until_ready)
    def wait_until_ready(self):
        state = SpallocState.UNKNOWN
        while state != SpallocState.READY:
            state = self.wait_for_state_change(state)
            if state == SpallocState.DESTROYED:
                raise Exception("job was unexpectedly destroyed")

    @overrides(SpallocJob.destroy)
    def destroy(self, reason="finished"):
        if self.__keepalive_handle:
            self.__keepalive_handle.close()
            self.__keepalive_handle = None
        self._delete(self._url, reason=reason)
        logger.info("deleted job at {}", self._url)

    @overrides(SpallocJob.keepalive)
    def keepalive(self):
        self._put(self._keepalive_url, "alive")

    @overrides(SpallocJob.launch_keepalive_task)
    def launch_keepalive_task(self, period=30):
        """
        .. note::
            Tricky! *Cannot* be done with a thread, as the main thread is known
            to do significant amounts of CPU-intensive work.
        """
        class Closer(AbstractContextManager):
            def __init__(self):
                self._queue = Queue(1)

            def close(self):
                self._queue.put("quit")

        self._keepalive_handle = Closer()
        p = Process(target=_SpallocKeepalive, args=(
            self._keepalive_url, period, self._keepalive_handle._queue,
            *self._session_credentials), daemon=True)
        p.start()
        return self._keepalive_handle

    @overrides(SpallocJob.where_is_machine)
    def where_is_machine(self, x: int, y: int) -> Tuple[int, int, int]:
        r = self._get(self.__chip_url, x=int(x), y=int(y))
        if r.status_code == 204:
            return None
        return tuple(r.json()["physical-board-coordinates"])

    @property
    def _keepalive_handle(self):
        return self.__keepalive_handle

    @_keepalive_handle.setter
    def _keepalive_handle(self, handle):
        if self.__keepalive_handle is not None:
            raise Exception("cannot keep job alive from two tasks")
        self.__keepalive_handle = handle

    @overrides(SpallocJob.create_transceiver)
    def create_transceiver(self, default_report_directory=None) -> Transceiver:
        if self.get_state() != SpallocState.READY:
            raise Exception("job not ready to execute scripts")
        proxies = [
            self.connect_to_board(x, y) for (x, y) in self.get_connections()]
        # Also need a boot connection
        proxies.append(self.connect_for_booting())
        return Transceiver(version=5, connections=proxies,
                           default_report_directory=default_report_directory)

    def __repr__(self):
        return f"SpallocJob({self._url})"


class _ProxiedConnection(metaclass=AbstractBase):
    """
    Core mux/demux emulating a connection that is proxied over a websocket.

    None of the methods are public because subclasses may expose a profile of
    them to conform to a particular type of connection.
    """
    __slots__ = (
        "__ws", "__receiver", "__msgs", "__call_queue", "__call_lock",
        "__handle", "__current_msg")

    def __init__(self, ws: WebSocket, receiver: _ProxyReceiver):
        self.__ws = ws
        self.__receiver = receiver
        self.__msgs = queue.Queue()
        self.__call_queue = queue.Queue(1)
        self.__call_lock = threading.RLock()
        self.__current_msg = None
        self.__handle, = self._open_connection()
        self.__receiver.listen(self.__handle, self.__msgs.put)

    @abstractmethod
    def _open_connection(self) -> int:
        pass

    def _call(self, proto: ProxyProtocol, packer: struct.Struct,
              unpacker: struct.Struct, *args) -> List[int]:
        if not self._connected:
            raise IOError("socket closed")
        with self.__call_lock:
            # All calls via websocket use correlation_id
            correlation_id = self.__receiver.expect_return(
                self.__call_queue.put)
            self.__ws.send_binary(packer.pack(proto, correlation_id, *args))
            return unpacker.unpack(self.__call_queue.get())[2:]

    @property
    def _connected(self) -> bool:
        return self.__ws and self.__ws.connected

    def _throw_if_closed(self):
        if not self._connected:
            raise IOError("socket closed")

    def _close(self):
        if self._connected:
            channel_id, = self.__call(
                ProxyProtocol.CLOSE, _close_req, _open_close_res,
                self.__handle)
            if channel_id != self.__handle:
                raise IOError("failed to close proxy socket")
        self.__ws = None
        self.__receiver = None

    def _send(self, message: bytes):
        self._throw_if_closed()
        # Put the header on the front and send it
        self.__ws.send_binary(_msg.pack(
            ProxyProtocol.MSG, self.__handle) + message)

    def _send_to(self, message: bytes, x: int, y: int, port: int):
        self._throw_if_closed()
        # Put the header on the front and send it
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

    def _receive(self, timeout=None) -> bytes:
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

    def _is_ready_to_receive(self, timeout=0) -> bool:
        # If we already have a message or the queue peek succeeds, return now
        if self.__current_msg is not None or self.__msgs.not_empty:
            return True
        try:
            self.__current_msg = self.__get(timeout)
            return True
        except queue.Empty:
            return False


class _ProxiedBidirectionalConnection(
        _ProxiedConnection, SpallocProxiedConnectionBase):
    __slots__ = ("__connect_args")

    def __init__(
            self, ws: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        self.__connect_args = (x, y, port)
        super().__init__(ws, receiver)

    @overrides(_ProxiedConnection._open_connection)
    def _open_connection(self):
        handle, = self.__call(
            ProxyProtocol.OPEN, _open_req, _open_close_res,
            *self.__connect_args)
        return handle

    @overrides(Connection.is_connected)
    def is_connected(self) -> bool:
        return self._connected

    @overrides(Connection.close)
    def close(self):
        self._close()

    @overrides(SpallocProxiedConnectionBase.send)
    def send(self, message: bytes):
        self._send(message)

    @overrides(SpallocProxiedConnectionBase.receive)
    def receive(self, timeout=None) -> bytes:
        return self._receive(timeout)

    @overrides(Listenable.is_ready_to_receive)
    def is_ready_to_receive(self, timeout=0) -> bool:
        return self._is_ready_to_receive(timeout)


class _ProxiedSCAMPConnection(
        _ProxiedBidirectionalConnection, SpallocProxiedConnection):
    __slots__ = ("_chip_x", "_chip_y")

    def __init__(
            self, ws: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        super().__init__(ws, receiver, x, y, port)
        self._chip_x = x
        self._chip_y = y

    @property
    @overrides(SCPSender.chip_x)
    def chip_x(self) -> int:
        return self._chip_x

    @property
    @overrides(SCPSender.chip_y)
    def chip_y(self) -> int:
        return self._chip_y

    def __str__(self):
        return f"SCAMPConnection[proxied]({self.chip_x},{self.chip_y})"


class _ProxiedBootConnection(
        _ProxiedBidirectionalConnection, SpallocBootConnection):
    __slots__ = ()

    def __init__(self, ws: WebSocket, receiver: _ProxyReceiver):
        super().__init__(ws, receiver, 0, 0, UDP_BOOT_CONNECTION_DEFAULT_PORT)

    def __str__(self):
        return "BootConnection[proxied]()"


class _ProxiedEIEIOConnection(
        _ProxiedBidirectionalConnection, SpallocProxiedConnectionBase,
        SpallocEIEIOConnection):
    # Special: This is a unidirectional receive-only connection
    __slots__ = ("__addr", "__port", "__chip_x", "__chip_y")

    def __init__(
            self, ws: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        super().__init__(ws, receiver, x, y, port)
        self.__chip_x = x
        self.__chip_y = y

    def send_to(self, message: bytes, address: tuple):  # @UnusedVariable
        """
        Direct ``send_to`` is unsupported.
        """
        self._throw_if_closed()
        raise IOError("socket is not open for sending")

    def __str__(self):
        return (f"EIEIOConnection[proxied](remote:{self.__chip_x},"
                f"{self.__chip_y})")


class _ProxiedEIEIOListener(
        _ProxiedConnection, SpallocProxiedConnectionBase,
        SpallocEIEIOListener):
    # Special: This is a unidirectional receive-only connection
    __slots__ = ("__addr", "__port", "__conns")

    def __init__(self, ws: WebSocket, receiver: _ProxyReceiver,
                 conns: Dict[Tuple[int, int], str]):
        super().__init__(ws, receiver)
        # Invert the map
        self.__conns = {ip: xy for (xy, ip) in conns.items()}

    @overrides(_ProxiedConnection._open_connection)
    def _open_connection(self) -> int:
        handle, ip1, ip2, ip3, ip4, self.__port = self.__call(
            ProxyProtocol.OPEN_UNBOUND, _open_listen_req, _open_listen_res)
        # Assemble the address into the format expected elsewhere
        self.__addr = f"{ip1}.{ip2}.{ip3}.{ip4}"
        return handle

    @overrides(Connection.is_connected)
    def is_connected(self) -> bool:
        return self._connected

    @overrides(Connection.close)
    def close(self):
        self._close()

    @overrides(SpallocProxiedConnectionBase.send)
    def send(self, message: bytes):  # @UnusedVariable
        self._throw_if_closed()
        raise IOError("socket is not open for sending")

    @overrides(SpallocEIEIOListener.send_to_chip)
    def send_to_chip(
            self, message: bytes, x: int, y: int, port: int = SCP_SCAMP_PORT):
        self._send_to(message, x, y, port)

    @overrides(SpallocProxiedConnectionBase.receive)
    def receive(self, timeout=None) -> bytes:
        return self._receive(timeout)

    @overrides(Listenable.is_ready_to_receive)
    def is_ready_to_receive(self, timeout=0) -> bool:
        return self._is_ready_to_receive(timeout)

    @property
    @overrides(SpallocEIEIOListener.local_ip_address)
    def local_ip_address(self) -> str:
        return self.__addr if self._connected else None

    @property
    @overrides(SpallocEIEIOListener.local_port)
    def local_port(self) -> int:
        return self.__port if self._connected else None

    @overrides(SpallocEIEIOListener._get_chip_coords)
    def _get_chip_coords(self, ip_address: str) -> Tuple[int, int]:
        return self.__conns[ip_address]

    def __str__(self):
        return (f"EIEIOConnection[proxied](local:{self.local_ip_address}:"
                f"{self.local_port})")
