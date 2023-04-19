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

from sqlite3 import Cursor
from typing import Dict, Tuple
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.abstract_context_manager import AbstractContextManager
from spinnman.constants import SCP_SCAMP_PORT
from spinnman.transceiver import Transceiver
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
            port: int = SCP_SCAMP_PORT) -> SpallocSCPConnection:
        """
        Open a connection to a particular board in the job.

        :param int x: X coordinate of the board's Ethernet-enabled chip
        :param int y: Y coordinate of the board's Ethernet-enabled chip
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

        :param int x:
            The X coordinate of the Ethernet-enabled chip to connect to
        :param int y:
            The Y coordinate of the Ethernet-enabled chip to connect to
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
        :return: The state that the allocation is now in.

            .. note::
                If the machine gets destroyed, this will not wait for it.
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
            Some kind of closable task handle; closing it terminates the task.
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

        .. note::
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
