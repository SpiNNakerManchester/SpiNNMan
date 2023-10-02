# Copyright (c) 2017 The University of Manchester
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

from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.enums import SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ChipSummaryInfo


class GetChipInfoResponse(AbstractSCPResponse):
    """
    An SCP response to a request for the version of software running.
    """
    __slots__ = [
        "_chip_info"]

    def __init__(self):
        super().__init__()
        self._chip_info = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Version", "CMD_CHIP_INFO", result.name)
        self._chip_info = ChipSummaryInfo(
            data, offset, self.sdp_header.source_chip_x,
            self.sdp_header.source_chip_y,)

    @property
    def chip_info(self):
        """
        The chip information received.

        :rtype: ChipSummaryInfo
        """
        return self._chip_info
