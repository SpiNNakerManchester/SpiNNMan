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
import contextlib
import struct
from typing import Callable, Dict, Iterable, Set, Tuple
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod, abstractproperty)
from spinn_utilities.overrides import overrides
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinnman.connections.abstract_classes import (
    Listenable, SDPReceiver, SDPSender, SCPReceiver, SCPSender)
from spinnman.connections.udp_packet_connections import (
    update_sdp_header_for_udp_send)
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.messages.sdp import SDPMessage, SDPFlag
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPResult
from spinnman.transceiver import Transceiver
from .enums import SpallocState

_TWO_SHORTS = struct.Struct("<2H")


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


class SpallocProxiedConnection(
        SDPReceiver, SDPSender, SCPSender, SCPReceiver, Listenable,
        metaclass=AbstractBase):
    """
    The socket interface supported by proxied sockets. The socket will always
    be talking to a specific board. This emulates a SCAMPConnection.
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
        """

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
        self.send(b'\0\0' + sdp_message.bytestring)

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
        return b'\0\0' + scp_request.bytestring


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


class SpallocJob(contextlib.AbstractContextManager, metaclass=AbstractBase):
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
    def create_transceiver(
            self, default_report_directory: str = None) -> Transceiver:
        """
        Create a transceiver that will talk to this job. The transceiver will
        only be configured to talk to the SCP ports of the boards of the job.

        :param str default_report_directory:
            Directory to write any reports too. If ``None`` the current
            directory will be used.
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
