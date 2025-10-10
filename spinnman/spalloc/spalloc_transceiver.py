# Copyright (c) 2025 The University of Manchester
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
import io
import os
import struct
from typing import List, Union, BinaryIO, Optional, Tuple, cast, Dict

import numpy
from numpy import uint8, uint32

from spinn_utilities.overrides import overrides

from spinnman.transceiver.version5transceiver import Version5Transceiver
from spinnman.connections.abstract_classes.connection import Connection
from spinnman.processes.write_memory_process import _UNSIGNED_WORD
from spinnman.model.diagnostic_filter import DiagnosticFilter

from .spalloc_job import SpallocJob

_ONE_WORD = struct.Struct("<I")


class SpallocTransceiver(Version5Transceiver):
    """ A transceiver for a Spalloc job, where some functions use spalloc more
        directly to speed up operation.
    """

    __slots__ = ["__job"]

    def __init__(self, job: SpallocJob, ensure_board_is_ready: bool = False):
        """ Create a Spalloc Transceiver.

        :param job: The job to use to communicate with the machine via Spalloc
        :param ensure_board_is_ready:
            Flag to say if ensure_board_is_ready should be run
        """
        self.__job: SpallocJob = job
        proxies: List[Connection] = [
            job.connect_to_board(x, y) for (x, y) in job.get_connections()]
        # Also need a boot connection
        proxies.append(job.connect_for_booting())

        super(SpallocTransceiver, self).__init__(
            connections=proxies, ensure_board_is_ready=ensure_board_is_ready)

    @overrides(Version5Transceiver.write_memory)
    def write_memory(
            self, x: int, y: int, base_address: int,
            data: Union[BinaryIO, bytes, int, str],
            *, n_bytes: Optional[int] = None, offset: int = 0, cpu: int = 0,
            get_sum: bool = False) -> Tuple[int, int]:

        if isinstance(data, io.RawIOBase):
            assert n_bytes is not None
            reader = cast(BinaryIO, data)
            data_array = reader.read(n_bytes)

        elif isinstance(data, str):
            if n_bytes is None:
                n_bytes = os.stat(data).st_size
            with open(data, "rb") as reader:
                data_array = reader.read(n_bytes)

        elif isinstance(data, int):
            n_bytes = 4
            data_array = _ONE_WORD.pack(data)

        else:
            assert isinstance(data, (bytes, bytearray))
            if n_bytes is None:
                n_bytes = len(data)
            data_array = bytes(data)

        self.__job.write_data(x, y, base_address, data_array)
        chksum = 0
        if get_sum:
            np_data = numpy.frombuffer(data_array, dtype=uint8)
            np_sum = int(numpy.sum(np_data.view(uint32), dtype=uint32))
            chksum = np_sum & _UNSIGNED_WORD

        return n_bytes, chksum

    @overrides(Version5Transceiver.read_memory)
    def read_memory(
            self, x: int, y: int, base_address: int, length: int,
            cpu: int = 0) -> bytearray:
        return bytearray(self.__job.read_data(x, y, base_address, length))

    @overrides(Version5Transceiver._do_reset_routing)
    def _do_reset_routing(
            self, custom_filters: Dict[int, DiagnosticFilter]) -> None:
        self.__job.reset_routing(custom_filters)

    def __str__(self) -> str:
        return f"Spalloc Transceiver over {self.__job}"
