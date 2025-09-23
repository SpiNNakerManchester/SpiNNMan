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
from typing import Dict, Iterable
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
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
