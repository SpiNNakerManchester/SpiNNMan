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
import struct
import threading
from typing import List, Tuple
from websocket import WebSocket
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
    SpallocMachine)
from spinnman.transceiver import Transceiver

logger = FormatAdapter(getLogger(__name__))
_open_req = struct.Struct("<IIIII")
_close_req = struct.Struct("<III")
# Open and close share the response structure
_open_close_res = struct.Struct("<III")
_msg = struct.Struct("<II")


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
            if code in (ProxyProtocol.OPEN, ProxyProtocol.CLOSE):
                self.dispatch_return(num, frame)
            else:
                self.dispatch_message(num, frame)

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


class _ProxiedConnection(SpallocProxiedConnectionBase):
    __slots__ = (
        "__ws", "__receiver", "__handle", "__msgs", "__current_msg",
        "__call_queue", "__call_lock")

    def __init__(
            self, ws: WebSocket, receiver: _ProxyReceiver,
            x: int, y: int, port: int):
        self.__ws = ws
        self.__receiver = receiver
        self.__msgs = queue.Queue()
        self.__current_msg = None
        self.__call_queue = queue.Queue(1)
        self.__call_lock = threading.RLock()
        self.__handle, = self.__call(
            ProxyProtocol.OPEN, _open_req, _open_close_res, x, y, port)
        self.__receiver.listen(self.__handle, self.__msgs.put)

    def __call(self, proto: ProxyProtocol, packer: struct.Struct,
               unpacker: struct.Struct, *args) -> List[int]:
        if not self.is_connected:
            raise IOError("socket closed")
        with self.__call_lock:
            # All calls via websocket use correlation_id
            correlation_id = self.__receiver.expect_return(
                self.__call_queue.put)
            self.__ws.send_binary(packer.pack(proto, correlation_id, *args))
            return unpacker.unpack(self.__call_queue.get())[2:]

    @overrides(Connection.is_connected)
    def is_connected(self) -> bool:
        return self.__ws and self.__ws.connected

    @overrides(Connection.close)
    def close(self):
        channel_id, = self.__call(
            ProxyProtocol.CLOSE, _close_req, _open_close_res, self.__handle)
        if channel_id != self.__handle:
            raise IOError("failed to close proxy socket")
        self.__ws = None
        self.__receiver = None

    @overrides(SpallocProxiedConnectionBase.send)
    def send(self, message: bytes):
        if not self.is_connected:
            raise IOError("socket closed")
        # Put the header on the front and send it
        self.__ws.send_binary(_msg.pack(
            ProxyProtocol.MSG, self.__handle) + message)

    def __get(self, timeout: float = 0.5) -> bytes:
        """
        Get a value from the queue. Handles block/non-block switching and
        trimming of the message protocol prefix.
        """
        if not timeout:
            return self.__msgs.get(block=False)[_msg.size:]
        else:
            return self.__msgs.get(timeout=timeout)[_msg.size:]

    @overrides(SpallocProxiedConnectionBase.receive)
    def receive(self, timeout=None) -> bytes:
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
                    pass
                if not self.is_connected:
                    raise IOError("socket closed")
        else:
            try:
                return self.__get(timeout)
            except queue.Empty as e:
                if not self.is_connected:
                    # pylint: disable=raise-missing-from
                    raise IOError("socket closed")
                raise SpinnmanTimeoutException("receive", timeout) from e

    @overrides(Listenable.is_ready_to_receive)
    def is_ready_to_receive(self, timeout=0) -> bool:
        # If we already have a message or the queue peek succeeds, return now
        if self.__current_msg is not None or self.__msgs.not_empty:
            return True
        try:
            self.__current_msg = self.__get(timeout)
            return True
        except queue.Empty:
            return False


class _ProxiedSCAMPConnection(_ProxiedConnection, SpallocProxiedConnection):
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


class _ProxiedBootConnection(_ProxiedConnection, SpallocBootConnection):
    __slots__ = ()

    def __init__(self, ws: WebSocket, receiver: _ProxyReceiver):
        super().__init__(ws, receiver, 0, 0, UDP_BOOT_CONNECTION_DEFAULT_PORT)
