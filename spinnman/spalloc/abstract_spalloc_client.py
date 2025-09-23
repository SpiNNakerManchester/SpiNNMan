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
"""
API of the client for the Spalloc web service.
"""

import struct
from typing import Never
from typing import Dict, Iterable, Tuple, Optional
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.exceptions import SpallocException
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
        """
        raise NotImplementedError

    @abstractmethod
    def list_jobs(self, deleted: bool = False) -> Iterable[SpallocJob]:
        """
        Get the jobs known to the server.

        :param deleted: Whether to include deleted jobs.
        :return: The jobs known to the server.
        """
        raise NotImplementedError

    @abstractmethod
    def create_job(self) -> SpallocJob:
        """
        Create a job with a specified number of boards.

        :return: A handle for monitoring and interacting with the job.
        """
        raise NotImplementedError

    def create_job_rect(
            self, width: int, height: int, machine_name: Optional[str] = None,
            keepalive: int = 45) -> Never:
        """
        No longer supported use create_job with cfg settings instead

        :param width:
            Use cfg "Machine", "spalloc_width" instead
        :param height:
            Use cfg "Machine", "spalloc_height" instead
        :param machine_name:
            Use cfg "Machine", "spalloc_machine" instead
        :param keepalive:
            No longer supported
        :raise: SpallocException
        """
        _ = (width, height, keepalive)
        error_st = ('create_job_rect is no longer supported. '
                    'Use create_job with cfg ("Machine") settings '
                    'spalloc_width and spalloc_height')
        if machine_name is None:
            error_st += " as well as spalloc_machine"
        raise SpallocException(error_st)

    def create_job_board(
            self, triad: Optional[Tuple[int, int, int]] = None,
            physical: Optional[Tuple[int, int, int]] = None,
            ip_address: Optional[str] = None,
            machine_name: Optional[str] = None,
            keepalive: int = 45) -> Never:
        """
        Create a job with a specific board. At least one of ``triad``,
        ``physical`` and ``ip_address`` must be not ``None``.

        :param triad:
            The logical coordinate of the board to request
        :param physical:
            The physical coordinate of the board to request
        :param ip_address:
            The IP address of the board to request
        :param machine_name:
            Which machine to run on? If omitted, the service's machine tagged
            with ``default`` will be used.
        :param keepalive:
            After how many seconds of no activity should a job become eligible
            for automatic pruning?
        :raise: SpallocException
        """
        raise NotImplementedError

    def create_job_rect_at_board(
            self, width: int, height: int,
            triad: Optional[Tuple[int, int, int]] = None,
            physical: Optional[Tuple[int, int, int]] = None,
            ip_address: Optional[str] = None,
            machine_name: Optional[str] = None, keepalive: int = 45,
            max_dead_boards: int = 0) -> SpallocJob:
        """
        Create a job with a rectangle of boards starting at a specific board.
        At least one of ``triad``, ``physical`` and ``ip_address`` must be not
        ``None``.

        :param width:
            The width of rectangle to request
        :param height:
            The height of rectangle to request
        :param triad:
            The logical coordinate of the board to request
        :param physical:
            The physical coordinate of the board to request
        :param ip_address:
            The IP address of the board to request
        :param machine_name:
            Which machine to run on? If omitted, the service's machine tagged
            with ``default`` will be used.
        :param keepalive:
            After how many seconds of no activity should a job become eligible
            for automatic pruning?
        :param max_dead_boards:
            How many dead boards can be included.
        :return: A handle for monitoring and interacting with the job.
        """
        raise NotImplementedError
