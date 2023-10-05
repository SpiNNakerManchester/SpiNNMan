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

import struct
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_BYTE_SKIP_BYTE_BYTE = struct.Struct("<Bx2B")


class IPTagGetInfoResponse(AbstractSCPResponse):
    """
    An SCP response to a request for information about IP tags.
    """
    __slots__ = [
        "_fixed_size",
        "_pool_size",
        "_tto"]

    def __init__(self):
        super().__init__()
        self._tto = None
        self._pool_size = None
        self._fixed_size = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Get IP Tag Info", "CMD_IPTAG", result.name)

        self._tto, self._pool_size, self._fixed_size = \
            _BYTE_SKIP_BYTE_BYTE.unpack_from(data, offset)

    @property
    def transient_timeout(self):
        """
        The timeout for transient IP tags (i.e. responses to SCP commands).

        :rtype: int
        """
        return self._tto

    @property
    def pool_size(self):
        """
        The count of the IP tag pool size.

        :rtype: int
        """
        return self._pool_size

    @property
    def fixed_size(self):
        """
        The count of the number of fixed IP tag entries.

        :rtype: int
        """
        return self._fixed_size
