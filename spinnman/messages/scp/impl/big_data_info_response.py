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

from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import BigDataInfo


class BigDataInfoResponse(AbstractSCPResponse):
    """ An SCP response to a request for the big data transfer information
    """
    __slots__ = ["_big_data_info"]

    def __init__(self):
        super(BigDataInfoResponse, self).__init__()
        self._big_data_info = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Get Big Data Information", "CMD_BIG_DATA", result.name)
        self._big_data_info = BigDataInfo(
            data, offset, self.sdp_header.source_chip_x,
            self.sdp_header.source_chip_y)

    @property
    def big_data_info(self):
        return self._big_data_info
