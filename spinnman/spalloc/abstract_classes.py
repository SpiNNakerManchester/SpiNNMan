# Copyright (c) 2022 The University of Manchester
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
API of the client for the Spalloc web service.
"""

from sqlite3 import Cursor
import struct
import time
from typing import Callable, Dict, Iterable, Set, Tuple
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod, abstractproperty)
from spinn_utilities.overrides import overrides
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinnman.connections.abstract_classes import (
    Listenable, SDPReceiver, SDPSender, SCPReceiver, SCPSender,
    SpinnakerBootReceiver, SpinnakerBootSender, EIEIOReceiver, EIEIOSender)
from spinnman.connections.udp_packet_connections import (
    update_sdp_header_for_udp_send)
from spinnman.connections.udp_packet_connections.boot_connection import (
    _ANTI_FLOOD_DELAY)
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.messages.eieio import (
    AbstractEIEIOMessage,
    read_eieio_command_message, read_eieio_data_message)
from spinnman.messages.sdp import SDPMessage, SDPFlag, SDPHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.impl import IPTagSet
from spinnman.messages.scp.enums import SCPResult
from spinnman.messages.spinnaker_boot import SpinnakerBootMessage
from spinnman.transceiver import Transceiver
from .enums import SpallocState

_ONE_SHORT = struct.Struct("<H")
_TWO_SHORTS = struct.Struct("<2H")
_TWO_SKIP: bytes = b'\0\0'
_NUM_UPDATE_TAG_TRIES = 3
_UPDATE_TAG_TIMEOUT = 1.0


class AbstractSpallocClient(object, metaclass=AbstractBase):
    """
    The API exported by the Spalloc Client.
    """
    __slots__ = ()

    @abstractmethod
    def list_machines(self) -> Dict[str, 'SpallocMachine']:
        """
        Get the machines supported by the server.

        :return:
            Mapping from machine names to handles for working with a machine.
        :rtype: dict(str,SpallocMachine)
        """

    @abstractmethod
    def list_jobs(self, deleted: bool = False) -> Iterable['SpallocJob']:
        """
        Get the jobs known to the server.

        :param bool deleted: Whether to include deleted jobs.
        :return: The jobs known to the server.
        :rtype: ~typing.Iterable(SpallocJob)
        """

    @abstractmethod
    def create_job(
            self, num_boards: int = 1, machine_name: str = None,
            keepalive: int = 45) -> 'SpallocJob':
        """
        Create a job with a specified number of boards.

        :param int num_boards:
            How many boards to ask for (defaults to 1)
        :param str machine_name:
            Which machine to run on? If omitted, the service's machine tagged
            with ``default`` will be used.
        :param int keepalive:
            After how many seconds of no activity should a job become eligible
            for automatic pruning?
        :return: A handle for monitoring and interacting with the job.
        :rtype: SpallocJob
        """

    @abstractmethod
    def create_job_rect(
            self, width: int, height: int, machine_name: str = None,
            keepalive: int = 45) -> 'SpallocJob':
        """
        Create a job with a rectangle of boards.

        :param int width:
            The width of rectangle to request
        :param int height:
            The height of rectangle to request
        :param str machine_name:
            Which machine to run on? If omitted, the service's machine tagged
            with ``default`` will be used.
        :param int keepalive:
            After how many seconds of no activity should a job become eligible
            for automatic pruning?
        :return: A handle for monitoring and interacting with the job.
        :rtype: SpallocJob
        """

    @abstractmethod
    def create_job_board(
            self, triad: Tuple[int, int, int] = None,
            physical: Tuple[int, int, int] = None, ip_address: str = None,
            machine_name: str = None, keepalive: int = 45) -> 'SpallocJob':
        """
        Create a job with a specific board. At least one of ``triad``,
        ``physical`` and ``ip_address`` must be not ``None``.

        :param tuple(int,int,int) triad:
            The logical coordinate of the board to request
        :param tuple(int,int,int) physical:
            The physical coordinate of the board to request
        :param str ip_address:
            The IP address of the board to request
        :param str machine_name:
            Which machine to run on? If omitted, the service's machine tagged
            with ``default`` will be used.
        :param int keepalive:
            After how many seconds of no activity should a job become eligible
            for automatic pruning?
        :return: A handle for monitoring and interacting with the job.
        :rtype: SpallocJob
        """


class SpallocProxiedConnectionBase(Listenable, metaclass=AbstractBase):
    """
    Base class for connections proxied via Spalloc.
    """
    __slots__ = ()

    @abstractmethod
    def send(self, message: bytes):
        """
        Send a message on an open socket.

        :param message: The message to send.
        """

    @abstractmethod
    def receive(self, timeout=None) -> bytes:
        """
        Receive a message on an open socket. Will block until a message is
        received.

        :param timeout:
            How long to wait for a message to be received before timing out.
            If None, will wait indefinitely (or until the connection is
            closed).
        :return: The received message.
        :raises SpinnmanTimeoutException:
            If a timeout happens
        """


class SpallocProxiedConnection(
        SpallocProxiedConnectionBase,
        SDPReceiver, SDPSender, SCPSender, SCPReceiver,
        metaclass=AbstractBase):
    """
    The socket interface supported by proxied sockets. The socket will always
    be talking to a specific board. This emulates a SCAMPConnection.
    """
    __slots__ = ()

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self) -> Callable:
        return self.receive_sdp_message

    @overrides(SDPReceiver.receive_sdp_message)
    def receive_sdp_message(self, timeout=None) -> SDPMessage:
        data = self.receive(timeout)
        return SDPMessage.from_bytestring(data, 2)

    @overrides(SDPSender.send_sdp_message)
    def send_sdp_message(self, sdp_message: SDPMessage):
        # If a reply is expected, the connection should
        if sdp_message.sdp_header.flags == SDPFlag.REPLY_EXPECTED:
            update_sdp_header_for_udp_send(
                sdp_message.sdp_header, self.chip_x, self.chip_y)
        else:
            update_sdp_header_for_udp_send(sdp_message.sdp_header, 0, 0)
        self.send(_TWO_SKIP + sdp_message.bytestring)

    @overrides(SCPReceiver.receive_scp_response)
    def receive_scp_response(
            self, timeout=1.0) -> Tuple[SCPResult, int, bytes, int]:
        data = self.receive(timeout)
        result, sequence = _TWO_SHORTS.unpack_from(data, 10)
        return SCPResult(result), sequence, data, 2

    @overrides(SCPSender.send_scp_request)
    def send_scp_request(self, scp_request: AbstractSCPRequest):
        self.send(self.get_scp_data(scp_request))

    @overrides(SCPSender.get_scp_data)
    def get_scp_data(self, scp_request: AbstractSCPRequest) -> bytes:
        update_sdp_header_for_udp_send(
            scp_request.sdp_header, self.chip_x, self.chip_y)
        return _TWO_SKIP + scp_request.bytestring


class SpallocEIEIOConnection(
        SpallocProxiedConnectionBase,
        EIEIOSender, EIEIOReceiver, metaclass=AbstractBase):
    """
    The socket interface supported by proxied EIEIO connected sockets.
    This emulates an EIEOConnection opened with a remote address specified.
    """
    __slots__ = ()

    @overrides(EIEIOSender.send_eieio_message)
    def send_eieio_message(self, eieio_message):
        # Not normally used, as packets need headers to go to SpiNNaker
        self.send(eieio_message.bytestring)

    def send_eieio_message_to_core(
            self, eieio_message: AbstractEIEIOMessage, x: int, y: int, p: int):
        sdp_message = SDPMessage(
            SDPHeader(
                flags=SDPFlag.REPLY_NOT_EXPECTED, tag=0,
                destination_port=1, destination_cpu=p,
                destination_chip_x=x, destination_chip_y=y,
                source_port=0, source_cpu=0,
                source_chip_x=0, source_chip_y=0),
            data=eieio_message.bytestring)
        self.send(_TWO_SKIP + sdp_message.bytestring)

    @overrides(EIEIOReceiver.receive_eieio_message)
    def receive_eieio_message(self, timeout=None):
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        return read_eieio_data_message(data, 0)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive_eieio_message

    @abstractproperty
    def _coords(self) -> Tuple[int, int]:
        """
        The X, Y coordinates of the chip this connection is connected to.

        :rtype: tuple(int,int)
        """

    def update_tag(self, tag: int):
        """
        Update the given tag on the connected ethernet chip to send messages to
        this connection.

        :param int tag: The tag ID to update
        :raises SpinnmanTimeoutException:
            If the message isn't handled within a reasonable timeout.
        :raises SpinnmanUnexpectedResponseCodeException:
            If the message is rejected by SpiNNaker/SCAMP.
        """
        x, y = self._coords
        request = IPTagSet(
            x, y, [0, 0, 0, 0], 0, tag, strip=True, use_sender=True)
        request.sdp_header.flags = SDPFlag.REPLY_EXPECTED_NO_P2P
        update_sdp_header_for_udp_send(request.sdp_header, x, y)
        data = _TWO_SKIP + request.bytestring
        for _try in range(_NUM_UPDATE_TAG_TRIES):
            try:
                self.send(data)
                response_data = self.receive(_UPDATE_TAG_TIMEOUT)
                request.get_scp_response().read_bytestring(
                    response_data, len(_TWO_SKIP))
                return
            except SpinnmanTimeoutException as e:
                if _try + 1 == _NUM_UPDATE_TAG_TRIES:
                    raise e


class SpallocEIEIOListener(
        SpallocProxiedConnectionBase,
        EIEIOReceiver, metaclass=AbstractBase):
    """
    The socket interface supported by proxied EIEIO listener sockets.
    This emulates an EIEOConnection opened with no address specified.
    """
    __slots__ = ()

    @overrides(EIEIOReceiver.receive_eieio_message)
    def receive_eieio_message(self, timeout=None):
        data = self.receive(timeout)
        header = _ONE_SHORT.unpack_from(data)[0]
        if header & 0xC000 == 0x4000:
            return read_eieio_command_message(data, 0)
        return read_eieio_data_message(data, 0)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive_eieio_message

    @overrides(SpallocProxiedConnectionBase.send)
    def send(self, message):
        """
        .. note::
            This class does not allow sending.
        """

    @abstractmethod
    def _get_chip_coords(self, ip_address: str) -> Tuple[int, int]:
        """
        Get the coordinates of a chip given its IP address.

        :param str ip_address: The IP address of an ethernet chip in the job.
        :return: Ethernet chip coordinates: X, Y
        :rtype: tuple(int, int)
        """

    @abstractmethod
    def send_to_chip(
            self, message: bytes, x: int, y: int, port: int = SCP_SCAMP_PORT):
        """
        Send a message on an open socket to a particular board.

        :param bytes message: The message to send.
        :param int x:
            The X coordinate of the ethernet chip to send the message to.
        :param int y:
            The Y coordinate of the ethernet chip to send the message to.
        :param int port:
            The UDP port on the ethernet chip to send the message to.
            Defaults to the SCP port.
        """

    def send_to(self, message: bytes, address: Tuple[str, int]):
        """
        Send a message on an open socket.

        :param bytes message: The message to send.
        :param tuple(str,int) address:
            Where to send it to. Must be the address of an ethernet chip on a
            board allocated to the job. Does not mean that SpiNNaker is
            listening on that port (but the SCP port is being listened to if
            the board is booted).
        """
        ip, port = address
        x, y = self._get_chip_coords(ip)
        self.send_to_chip(message, x, y, port)

    @abstractproperty
    def local_ip_address(self) -> str:
        """ The IP address on the server to which the connection is bound.

        :return: The IP address as a dotted string, e.g., 0.0.0.0
        :rtype: str
        """

    @abstractproperty
    def local_port(self) -> int:
        """ The port on the server to which the connection is bound.

        :return: The local port number
        :rtype: int
        """

    def send_eieio_message_to_core(
            self, eieio_message: AbstractEIEIOMessage, x: int, y: int, p: int,
            ip_address: str):
        """
        Send an EIEIO message (one way) to a given core.

        :param AbstractEIEIOMessage eieio_message:
            The message to send.
        :param int x:
            The X coordinate of the core to send to.
        :param int y:
            The Y coordinate of the core to send to.
        :param int p:
            The ID of the core to send to.
        :param str ip_address:
            The IP address of the ethernet chip to route the message via.
        """
        sdp_message = SDPMessage(
            SDPHeader(
                flags=SDPFlag.REPLY_NOT_EXPECTED, tag=0,
                destination_port=1, destination_cpu=p,
                destination_chip_x=x, destination_chip_y=y,
                source_port=0, source_cpu=0,
                source_chip_x=0, source_chip_y=0),
            data=eieio_message.bytestring)
        self.send_to(
            _TWO_SKIP + sdp_message.bytestring, (ip_address, SCP_SCAMP_PORT))

    def update_tag(self, x: int, y: int, tag: int):
        """
        Update the given tag on the given ethernet chip to send messages to
        this connection.

        :param int x: The ethernet chip's X coordinate
        :param int y: The ethernet chip's Y coordinate
        :param int tag: The tag ID to update
        :raises SpinnmanTimeoutException:
            If the message isn't handled within a reasonable timeout.
        :raises SpinnmanUnexpectedResponseCodeException:
            If the message is rejected by SpiNNaker/SCAMP.
        """
        request = IPTagSet(
            x, y, [0, 0, 0, 0], 0, tag, strip=True, use_sender=True)
        request.sdp_header.flags = SDPFlag.REPLY_EXPECTED_NO_P2P
        update_sdp_header_for_udp_send(request.sdp_header, x, y)
        data = _TWO_SKIP + request.bytestring
        for _try in range(_NUM_UPDATE_TAG_TRIES):
            try:
                self.send_to_chip(data, x, y, SCP_SCAMP_PORT)
                response_data = self.receive(_UPDATE_TAG_TIMEOUT)
                request.get_scp_response().read_bytestring(
                    response_data, len(_TWO_SKIP))
                return
            except SpinnmanTimeoutException as e:
                if _try + 1 == _NUM_UPDATE_TAG_TRIES:
                    raise e

    def update_tag_by_ip(self, ip_address: str, tag: int):
        """
        Update a tag on a board at a given IP address to send messages to this
        connection.

        :param str ip_address: The address of the ethernet chip
        :param int tag: The ID of the tag
        """
        x, y = self._get_chip_coords(ip_address)
        self.update_tag(x, y, tag)


class SpallocBootConnection(
        SpallocProxiedConnectionBase,
        SpinnakerBootSender, SpinnakerBootReceiver, metaclass=AbstractBase):
    """
    The socket interface supported by proxied boot sockets. The socket will
    always be talking to the root board of a job.
    This emulates a BootConnection.
    """
    __slots__ = ()

    @overrides(SpinnakerBootSender.send_boot_message)
    def send_boot_message(self, boot_message: SpinnakerBootMessage):
        self.send(boot_message.bytestring)

        # Sleep between messages to avoid flooding the machine
        time.sleep(_ANTI_FLOOD_DELAY)

    @overrides(SpinnakerBootReceiver.receive_boot_message)
    def receive_boot_message(self, timeout=None) -> SpinnakerBootMessage:
        data = self.receive(timeout)
        return SpinnakerBootMessage.from_bytestring(data, 0)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self) -> Callable:
        return self.receive_boot_message


class SpallocMachine(object, metaclass=AbstractBase):
    """
    Represents a spalloc-controlled machine.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ()

    @abstractproperty
    def name(self) -> str:
        """
        The name of the machine.
        """

    @abstractproperty
    def tags(self) -> Set[str]:
        """
        The tags of the machine.
        """

    @abstractproperty
    def width(self) -> int:
        """
        The width of the machine, in boards.
        """

    @abstractproperty
    def height(self) -> int:
        """
        The height of the machine, in boards.
        """

    @abstractproperty
    def dead_boards(self) -> list:
        """
        The dead or out-of-service boards of the machine.
        """

    @abstractproperty
    def dead_links(self) -> list:
        """
        The dead or out-of-service links of the machine.
        """

    @abstractproperty
    def area(self) -> Tuple[int, int]:
        """
        Area of machine, in boards.

        :return: width, height
        :rtype: tuple(int,int)
        """


class SpallocJob(object, metaclass=AbstractBase):
    """
    Represents a job in spalloc.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ()

    @abstractmethod
    def get_state(self) -> SpallocState:
        """
        Get the current state of the machine.

        :rtype: SpallocState
        """

    @abstractmethod
    def get_root_host(self) -> str:
        """
        Get the IP address for talking to the machine.

        :return: The IP address, or ``None`` if not allocated.
        :rtype: str or None
        """

    @abstractmethod
    def get_connections(self) -> Dict[Tuple[int, int], str]:
        """
        Get the mapping from board coordinates to IP addresses.

        :return: (x,y)->IP mapping, or ``None`` if not allocated
        :rtype: dict(tuple(int,int), str) or None
        """

    @abstractmethod
    def connect_to_board(
            self, x: int, y: int,
            port: int = SCP_SCAMP_PORT) -> SpallocProxiedConnection:
        """
        Open a connection to a particular board in the job.

        :param int x: X coordinate of the board's ethernet chip
        :param int y: Y coordinate of the board's ethernet chip
        :param int port: UDP port to talk to; defaults to the SCP port
        :return: A connection that talks to the board.
        :rtype: SpallocProxiedConnection
        """

    @abstractmethod
    def connect_for_booting(self) -> SpallocBootConnection:
        """
        Open a connection to a job's allocation so it can be booted.

        :return: a boot connection
        :rtype: SpallocBootConnection
        """

    @abstractmethod
    def open_eieio_connection(self, x: int, y: int) -> SpallocEIEIOConnection:
        """
        Open an EIEIO connection to a specific board in a job.

        :param int x: The X coordinate of the ethernet chip to connect to
        :param int y: The Y coordinate of the ethernet chip to connect to
        :return: an EIEIO connection with a board address bound
        :rtype: SpallocEIEIOConnection
        """

    @abstractmethod
    def open_listener_connection(self) -> SpallocEIEIOListener:
        """
        Open a listening EIEIO connection to the job's boards. Messages cannot
        be sent on this connection unless you say which board to send to, but
        they can be received from all boards. You can also get the *server*
        side connection information so you can program that into a tag.

        :return: an EIEIO connection with no board address bound
        :rtype: SpallocEIEIOListener
        """

    @abstractmethod
    def create_transceiver(self) -> Transceiver:
        """
        Create a transceiver that will talk to this job. The transceiver will
        only be configured to talk to the SCP ports of the boards of the job.

        :rtype: Transceiver
        """

    @abstractmethod
    def wait_for_state_change(self, old_state: SpallocState) -> SpallocState:
        """
        Wait until the allocation is not in the given old state.

        :param SpallocState old_state:
            The state that we are looking to change out of.
        :return: The state that the allocation is now in. Note that if the
            machine gets destroyed, this will not wait for it.
        :rtype: SpallocState
        """

    @abstractmethod
    def wait_until_ready(self):
        """
        Wait until the allocation is in the ``READY`` state.

        :raises Exception: If the allocation is destroyed
        """

    @abstractmethod
    def destroy(self, reason: str = "finished"):
        """
        Destroy the job.

        :param str reason: Why the job is being destroyed.
        """

    @abstractmethod
    def keepalive(self):
        """
        Signal the job that we want it to stay alive for a while longer.
        """

    @abstractmethod
    def launch_keepalive_task(
            self, period: int = 30) -> AbstractContextManager:
        """
        Starts a periodic task to keep a job alive.

        :param SpallocJob job:
            The job to keep alive
        :param int period:
            How often to send a keepalive message (in seconds)
        :return:
            Some kind of closeable task handle; closing it terminates the task.
            Destroying the job will also terminate the task.
        """

    @abstractmethod
    def where_is_machine(self, x: int, y: int) -> Tuple[int, int, int]:
        """
        Get the *physical* coordinates of the board hosting the given chip.

        :param int x: Chip X coordinate
        :param int y: Chip Y coordinate
        :return: physical board coordinates (cabinet, frame, board), or
            ``None`` if there are no boards currently allocated to the job or
            the chip lies outside the allocation.
        :rtype: tuple(int,int,int) or None
        """

    @abstractmethod
    def _write_session_credentials_to_db(self, cur: Cursor):
        """
        Write the session credentials for the job to the database accessed by
        the given cursor.

        .. note ::
            May assume that there is a ``proxy_configuration`` table with
            ``kind``, ``name`` and ``value`` columns.

        :param ~sqlite3.Cursor cur:
            The open cursor to the database.
        """

    def __enter__(self):
        """
        Return self on entering context.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Handle exceptions by killing the job and logging the exception in the
        job's destroy reason.
        """
        try:
            self.destroy(str(exc_value))
        except Exception:  # pylint: disable=broad-except
            # Ignore this exception; there's not much we can do with it
            pass
        return None
