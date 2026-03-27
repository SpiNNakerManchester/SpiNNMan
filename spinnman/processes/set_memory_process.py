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
import struct
from typing import List, Tuple

from spinn_utilities.progress_bar import ProgressBar

from spinnman.processes.abstract_multi_connection_process import (
    AbstractMultiConnectionProcess)
from spinnman.messages.scp.impl.check_ok_response import CheckOKResponse
from spinnman.messages.scp.impl.write_memory import WriteMemory

_ONE_WORD = struct.Struct("<I")


class SetMemoryProcess(AbstractMultiConnectionProcess[CheckOKResponse]):
    """ A Process to set a single word of memory on a set of cores
    """

    def set_values(
            self, values: List[Tuple[int, int, int, int]],
            description: str) -> None:
        """ Set the memory values selected

        :param values: A list of x, y, address and value to set
        :param description: A description of the operation
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        progress = ProgressBar(len(values), description)
        for x, y, addr, value in progress.over(values):
            data_to_write = _ONE_WORD.pack(value)
            self._send_request(WriteMemory((x, y, 0), addr, data_to_write))
        self._finish()
        self.check_for_error()
        progress.end()
