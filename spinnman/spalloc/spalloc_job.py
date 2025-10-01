# Copyright (c) 2022 The University of Manchester
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

from contextlib import AbstractContextManager
from types import TracebackType
from typing import Dict, Mapping, Optional, Tuple, Type
from typing_extensions import Literal, Self

from spinn_utilities.abstract_base import abstractmethod
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.transceiver.transceiver import Transceiver
from spinnman.connections.udp_packet_connections import UDPConnection
from spinnman.model.diagnostic_filter import DiagnosticFilter
from .spalloc_state import SpallocState
from .spalloc_boot_connection import SpallocBootConnection
from .spalloc_eieio_connection import SpallocEIEIOConnection
from .spalloc_eieio_listener import SpallocEIEIOListener
from .spalloc_scp_connection import SpallocSCPConnection


class SpallocJob(AbstractContextManager):
    """
    Represents a job in Spalloc.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ()

    @abstractmethod
    def get_state(self, wait_for_change: bool = False) -> SpallocState:
        """
        Get the current state of the machine.

        :param wait_for_change: Whether to wait for a change in state
        :returns: The current or new state
        """
        raise NotImplementedError()

    @abstractmethod
    def get_root_host(self) -> Optional[str]:
        """
        Get the IP address for talking to the machine.

        :return: The IP address, or ``None`` if not allocated.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_connections(self) -> Dict[Tuple[int, int], str]:
        """
        Get the mapping from board coordinates to IP addresses.

        :return: (x,y)->IP mapping, or ``None`` if not allocated
        """
        raise NotImplementedError()

    @abstractmethod
    def connect_to_board(
            self, x: int, y: int,
            port: int = SCP_SCAMP_PORT) -> SpallocSCPConnection:
        """
        Open a connection to a particular board in the job.

        :param x: X coordinate of the board's Ethernet-enabled chip
        :param y: Y coordinate of the board's Ethernet-enabled chip
        :param port: UDP port to talk to; defaults to the SCP port
        :return: A connection that talks to the board.
        """
        raise NotImplementedError()

    @abstractmethod
    def connect_for_booting(self) -> SpallocBootConnection:
        """
        Open a connection to a job's allocation so it can be booted.

        :return: a boot connection
        """
        raise NotImplementedError()

    @abstractmethod
    def open_eieio_connection(self, x: int, y: int) -> SpallocEIEIOConnection:
        """
        Open an EIEIO connection to a specific board in a job.

        :param x:
            The X coordinate of the Ethernet-enabled chip to connect to
        :param y:
            The Y coordinate of the Ethernet-enabled chip to connect to
        :return: an EIEIO connection with a board address bound
        """
        raise NotImplementedError()

    @abstractmethod
    def open_eieio_listener_connection(self) -> SpallocEIEIOListener:
        """
        Open a listening EIEIO connection to the job's boards. Messages cannot
        be sent on this connection unless you say which board to send to, but
        they can be received from all boards. You can also get the *server*
        side connection information so you can program that into a tag.

        :return: an EIEIO connection with no board address bound
        """
        raise NotImplementedError()

    @abstractmethod
    def open_udp_listener_connection(self) -> UDPConnection:
        """
        Open a listening UDP connection to the job's boards. Messages cannot
        be sent on this connection unless you say which board to send to, but
        they can be received from all boards. You can also get the *server*
        side connection information so you can program that into a tag.

        :return: a UDP connection with no board address bound
        """
        raise NotImplementedError()

    @abstractmethod
    def create_transceiver(
            self, ensure_board_is_ready: bool = True) -> Transceiver:
        """
        Create a transceiver that will talk to this job. The transceiver will
        only be configured to talk to the SCP ports of the boards of the job.

        :param ensure_board_is_ready:
            Flag to say if ensure_board_is_ready should be run
        :returns: Transceiver that uses this job.
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_for_state_change(self, old_state: SpallocState,
                              timeout: Optional[int] = None) -> SpallocState:
        """
        Wait until the allocation is not in the given old state.

        :param old_state:
            The state that we are looking to change out of.
        :param timeout:
            The time to wait, or None to wait forever
        :return: The state that the allocation is now in.

            .. note::
                If the machine gets destroyed, this will not wait for it.
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_until_ready(self) -> None:
        """
        Wait until the allocation is in the ``READY`` state.

        :raises SpallocException: If the allocation is destroyed
        :raises SSpallocBoardUnavailableException:
            If a job for specific boards are disabled, in use or just wrong
        """
        raise NotImplementedError()

    @abstractmethod
    def destroy(self, reason: str = "finished") -> None:
        """
        Destroy the job.

        :param reason: Why the job is being destroyed.
        """
        raise NotImplementedError()

    @abstractmethod
    def where_is_machine(self, x: int, y: int) -> Optional[
            Tuple[int, int, int]]:
        """
        Get the *physical* coordinates of the board hosting the given chip.

        :param x: Chip X coordinate
        :param y: Chip Y coordinate
        :return: physical board coordinates (cabinet, frame, board), or
            ``None`` if there are no boards currently allocated to the job or
            the chip lies outside the allocation.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_session_credentials_for_db(self) -> Mapping[Tuple[str, str], str]:
        """
        Get the session credentials for the job to be written into a database

        These are the "COOKIE" "HEADER" items,
        .. note::
            May assume that there is a ``proxy_configuration`` table with
            ``kind``, ``name`` and ``value`` columns.

        :returns: Mapping of Tuple["COOKIE" or "HEADER", and the key]
            to the value for that key
        """
        raise NotImplementedError()

    @abstractmethod
    def write_data(self, x: int, y: int, address: int, data: bytes) -> None:
        """
        Write data to a given address on a given chip of the job.

        :param x: The X coordinate of the chip
        :param y: The Y coordinate of the chip
        :param address: The address to write to
        :param data: The data to write
        """
        raise NotImplementedError()

    @abstractmethod
    def read_data(self, x: int, y: int, address: int, size: int) -> bytes:
        """
        Write data to a given address on a given chip of the job.

        :param x: The X coordinate of the chip
        :param y: The Y coordinate of the chip
        :param address: The address to write to
        :param size: The number of bytes to read
        :return: The data read
        """
        raise NotImplementedError()

    @abstractmethod
    def reset_routing(
            self, custom_filters: Dict[int, DiagnosticFilter]) -> None:
        """
        Clear the routes, reset diagnostic counters and optionally set filters.

        :param custom_filters: Map of router filter id to filter to set.
        """
        raise NotImplementedError()

    def __enter__(self) -> Self:
        """
        Return self on entering context.
        """
        return self

    def __exit__(self, exc_type: Optional[Type],
                 exc_value: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> Literal[False]:
        """
        Handle exceptions by killing the job and logging the exception in the
        job's destroy reason.
        """
        try:
            self.destroy(str(exc_value))
        except Exception:  # pylint: disable=broad-except
            # Ignore this exception; there's not much we can do with it
            pass
        return False
