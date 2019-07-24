# Copyright (c) 2017-2019 The University of Manchester
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

import struct
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_BYTE_SKIP_BYTE_BYTE = struct.Struct("<Bx2B")


class IPTagGetInfoResponse(AbstractSCPResponse):
    """ An SCP response to a request for information about IP tags
    """
    __slots__ = [
        "_fixed_size",
        "_pool_size",
        "_tto"]

    def __init__(self):
        super(IPTagGetInfoResponse, self).__init__()
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
        """ The timeout for transient IP tags (i.e. responses to SCP commands)

        :rtype: int
        """
        return self._tto

    @property
    def pool_size(self):
        """ The count of the IP tag pool size

        :rtype: int
        """
        return self._pool_size

    @property
    def fixed_size(self):
        """ The count of the number of fixed IP tag entries

        :rtype: int
        """
        return self._fixed_size
