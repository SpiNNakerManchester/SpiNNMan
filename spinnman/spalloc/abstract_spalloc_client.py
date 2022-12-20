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

import struct
from typing import Dict, Iterable, Tuple
from spinn_utilities.abstract_base import (AbstractBase, abstractmethod)
from .spalloc_machine import SpallocMachine
from .spalloc_job import SpallocJob

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
    def list_machines(self) -> Dict[str, SpallocMachine]:
        """
        Get the machines supported by the server.

        :return:
            Mapping from machine names to handles for working with a machine.
        :rtype: dict(str,SpallocMachine)
        """

    @abstractmethod
    def list_jobs(self, deleted: bool = False) -> Iterable[SpallocJob]:
        """
        Get the jobs known to the server.

        :param bool deleted: Whether to include deleted jobs.
        :return: The jobs known to the server.
        :rtype: ~typing.Iterable(SpallocJob)
        """

    @abstractmethod
    def create_job(
            self, num_boards: int = 1, machine_name: str = None,
            keepalive: int = 45) -> SpallocJob:
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
            keepalive: int = 45) -> SpallocJob:
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
            machine_name: str = None, keepalive: int = 45) -> SpallocJob:
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
