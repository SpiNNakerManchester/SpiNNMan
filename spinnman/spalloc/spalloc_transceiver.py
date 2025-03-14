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
import numpy
from numpy import uint8, uint32
from typing import List, Union, BinaryIO, Optional, Tuple, cast, Dict

from spinn_utilities.overrides import overrides

from spinnman.transceiver.base_transceiver import BaseTransceiver
from spinnman.connections.abstract_classes.connection import Connection
from spinnman.processes.write_memory_process import _UNSIGNED_WORD
from spinnman.model.diagnostic_filter import DiagnosticFilter

from .spalloc_job import SpallocJob

_ONE_WORD = struct.Struct("<I")


class SpallocTransceiver(BaseTransceiver):
    """ A transceiver for a Spalloc job, where some functions use spalloc more
        directly to speed up operation.
    """

    __slots__ = ["__job"]

    def __init__(self, job: SpallocJob):
        """ Create a Spalloc Transceiver.

        :param job: The job to use to communicate with the machine via Spalloc
        """
        self.__job: SpallocJob = job
        proxies: List[Connection] = [
            job.connect_to_board(x, y) for (x, y) in job.get_connections()]
        # Also need a boot connection
        proxies.append(job.connect_for_booting())

        super(SpallocTransceiver, self).__init__(connections=proxies)

    @property
    @overrides(BaseTransceiver.boot_led_0_value)
    def boot_led_0_value(self) -> int:
        return 0x00000001

    @overrides(BaseTransceiver.write_memory)
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

    @overrides(BaseTransceiver.read_memory)
    def read_memory(
            self, x: int, y: int, base_address: int, length: int,
            cpu: int = 0) -> bytearray:
        return bytearray(self.__job.read_data(x, y, base_address, length))

    @overrides(BaseTransceiver.prepare_routing_tables)
    def prepare_routing_tables(
        self, custom_filters:Optional[
            Dict[int, DiagnosticFilter]] = None) -> None:
        self.__job.prepare_routers(custom_filters)
