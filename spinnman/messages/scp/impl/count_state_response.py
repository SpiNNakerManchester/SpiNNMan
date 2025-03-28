# Copyright (c) 2014 The University of Manchester
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

from typing import Optional
import struct
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_ONE_WORD = struct.Struct("<I")


class CountStateResponse(AbstractSCPResponse):
    """
    An SCP response to a request for the number of cores in a given state.
    """
    __slots__ = "_count",

    def __init__(self) -> None:
        super().__init__()
        self._count: Optional[int] = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        result = self.scp_response_header.result
        # We can accept a no-reply response here; that could just mean
        # that the count wasn't complete (but might be enough anyway)
        if result != SCPResult.RC_OK and result != SCPResult.RC_P2P_NOREPLY:
            raise SpinnmanUnexpectedResponseCodeException(
                "CountState", "CMD_COUNT", result.name)
        self._count = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def count(self) -> int:
        """
        The count of the number of cores with the requested state.

        """
        assert self._count is not None
        return self._count
