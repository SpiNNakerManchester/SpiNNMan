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
from spinnman.messages.scp.enums import SCPResult

_TWO_SHORTS = struct.Struct("<2H")


class SCPResponseHeader(object):
    """
    Represents the header of an SCP Response.
    """
    __slots__ = [
        "_result",
        "_sequence"]

    def __init__(self, result=None, sequence=None):
        """
        :param SCPResult result:
        :param int sequence:
        """
        self._result = result
        self._sequence = sequence

    @property
    def result(self):
        """
        The result of the SCP response.

        :rtype: SCPResult
        """
        return self._result

    @property
    def sequence(self):
        """
        The sequence number of the SCP response, between 0 and 65535.

        :rtype: int
        """
        return self._sequence

    @staticmethod
    def from_bytestring(data, offset):
        """
        Read a header from a byte-string.

        :param bytes data: The byte-string to read from
        :param int offset:
        """
        result, sequence = _TWO_SHORTS.unpack_from(data, offset)
        return SCPResponseHeader(SCPResult(result), sequence)
