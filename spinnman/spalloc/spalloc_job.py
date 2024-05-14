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

from typing import Dict, Mapping, Optional, Tuple
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.transceiver.transceiver import Transceiver
from spinnman.connections.udp_packet_connections import UDPConnection
from .spalloc_state import SpallocState
from .spalloc_boot_connection import SpallocBootConnection
from .spalloc_eieio_connection import SpallocEIEIOConnection
from .spalloc_eieio_listener import SpallocEIEIOListener
from .spalloc_scp_connection import SpallocSCPConnection


class SpallocJob(object, metaclass=AbstractBase):
    """
    Represents a job in Spalloc.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ()

    @abstractmethod
    def get_state(self, wait_for_change: bool = False) -> SpallocState:
        """
        Get the current state of the machine.

        :param bool wait_for_change: Whether to wait for a change in state

        :rtype: SpallocState
        """
        raise NotImplementedError()

    @abstractmethod
    def get_root_host(self) -> Optional[str]:
        """
        Get the IP address for talking to the machine.

        :return: The IP address, or ``None`` if not allocated.
        :rtype: str or None
        """
        raise NotImplementedError()

    @abstractmethod
    def get_connections(self) -> Dict[Tuple[int, int], str]:
        """
        Get the mapping from board coordinates to IP addresses.

        :return: (x,y)->IP mapping, or ``None`` if not allocated
        :rtype: dict(tuple(int,int), str) or None
        """
        raise NotImplementedError()

    @abstractmethod
    def connect_to_board(
            self, x: int, y: int,
            port: int = SCP_SCAMP_PORT) -> SpallocSCPConnection:
        """
        Open a connection to a particular board in the job.

        :param int x: X coordinate of the board's Ethernet-enabled chip
        :param int y: Y coordinate of the board's Ethernet-enabled chip
        :param int port: UDP port to talk to; defaults to the SCP port
        :return: A connection that talks to the board.
        :rtype: SpallocProxiedConnection
        """
        raise NotImplementedError()

    @abstractmethod
    def connect_for_booting(self) -> SpallocBootConnection:
        """
        Open a connection to a job's allocation so it can be booted.

        :return: a boot connection
        :rtype: SpallocBootConnection
        """
        raise NotImplementedError()

    @abstractmethod
    def open_eieio_connection(self, x: int, y: int) -> SpallocEIEIOConnection:
        """
        Open an EIEIO connection to a specific board in a job.

        :param int x:
            The X coordinate of the Ethernet-enabled chip to connect to
        :param int y:
            The Y coordinate of the Ethernet-enabled chip to connect to
        :return: an EIEIO connection with a board address bound
        :rtype: SpallocEIEIOConnection
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
        :rtype: SpallocEIEIOListener
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
        :rtype: UDPConnection
        """
        raise NotImplementedError()

    @abstractmethod
    def create_transceiver(self) -> Transceiver:
        """
        Create a transceiver that will talk to this job. The transceiver will
        only be configured to talk to the SCP ports of the boards of the job.

        :rtype: Transceiver
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_for_state_change(self, old_state: SpallocState,
                              timeout: Optional[int] = None) -> SpallocState:
        """
        Wait until the allocation is not in the given old state.

        :param SpallocState old_state:
            The state that we are looking to change out of.
        :param timeout:
            The time to wait, or None to wait forever
        :type timeout: int or None
        :return: The state that the allocation is now in.

            .. note::
                If the machine gets destroyed, this will not wait for it.
        :rtype: SpallocState
        """
        raise NotImplementedError()

    @abstractmethod
    def wait_until_ready(self, timeout: Optional[int] = None,
                         n_retries: Optional[int] = None):
        """
        Wait until the allocation is in the ``READY`` state.

        :param timeout: The timeout or None to wait forever
        :type timeout: int or None
        :param n_retries:
            The number of times to retry, or None to retry forever
        :type n_retries: int or None
        :raises Exception: If the allocation is destroyed
        """
        raise NotImplementedError()

    @abstractmethod
    def destroy(self, reason: str = "finished"):
        """
        Destroy the job.

        :param str reason: Why the job is being destroyed.
        """
        raise NotImplementedError()

    @abstractmethod
    def where_is_machine(self, x: int, y: int) -> Optional[
            Tuple[int, int, int]]:
        """
        Get the *physical* coordinates of the board hosting the given chip.

        :param int x: Chip X coordinate
        :param int y: Chip Y coordinate
        :return: physical board coordinates (cabinet, frame, board), or
            ``None`` if there are no boards currently allocated to the job or
            the chip lies outside the allocation.
        :rtype: tuple(int,int,int) or None
        """
        raise NotImplementedError()

    @abstractmethod
    def get_session_credentials_for_db(self) -> Mapping[Tuple[str, str], str]:
        """
        Get the session credentials for the job to be written into a database

        .. note::
            May assume that there is a ``proxy_configuration`` table with
            ``kind``, ``name`` and ``value`` columns.
        """
        raise NotImplementedError()

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
