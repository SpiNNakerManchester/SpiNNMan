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
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinnman.messages.sdp import SDPHeader
from spinnman.messages.scp import SCPResponseHeader

# The offset of the header from the start of a received packet
# (8 bytes of SDP header)
_SCP_HEADER_OFFSET = 8

# The offset of the data from the start of a received packet
# (8 bytes of SDP header + 4 bytes of SCP header)
_SCP_DATA_OFFSET = 12


class AbstractSCPResponse(object, metaclass=AbstractBase):
    """
    Represents an abstract SCP Response.
    """
    __slots__ = (
        "_scp_response_header",
        "_sdp_header")

    def __init__(self) -> None:
        self._sdp_header: Optional[SDPHeader] = None
        self._scp_response_header: Optional[SCPResponseHeader] = None

    def read_bytestring(self, data: bytes, offset: int) -> None:
        """
        Reads a packet from a byte-string of data.

        :param data: The byte-string to be read
        :param offset:
            The offset in the data from which the response should be read
        """
        self._sdp_header = SDPHeader.from_bytestring(data, offset)
        self._scp_response_header = SCPResponseHeader.from_bytestring(
            data, _SCP_HEADER_OFFSET + offset)
        self.read_data_bytestring(data, _SCP_DATA_OFFSET + offset)

    @abstractmethod
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        """
        Reads the remainder of the data following the header.

        :param data: The byte-string to read from
        :param offset: The offset into the data after the headers
        """
        raise NotImplementedError

    @property
    def sdp_header(self) -> SDPHeader:
        """ The SDP header from the response. """
        assert self._sdp_header is not None, "no response read"
        return self._sdp_header

    @property
    def scp_response_header(self) -> SCPResponseHeader:
        """ The SCP header from the response. """
        assert self._scp_response_header is not None, "no response read"
        return self._scp_response_header
