# Copyright (c) 2015 The University of Manchester
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
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse, BMPRequest, BMPResponse)
from spinnman.messages.scp.enums import BMPInfo, SCPCommand, SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ADCInfo


class ReadADC(BMPRequest):
    """
    SCP Request for the data from the BMP including voltages and
    temperature.

    This class is currently deprecated and untested as there is no
    known use except for Transceiver.read_adc_data which is itself
    deprecated.

    .. note::
        The equivalent code in Java is *not* deprecated.
    """
    __slots__ = []

    def __init__(self, board):
        """
        :param int board: which board to request the ADC register from
        """
        super().__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=BMPInfo.ADC)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPReadADCResponse()


class _SCPReadADCResponse(BMPResponse):
    """
    An SCP response to a request for ADC information.
    """
    __slots__ = [
        "_adc_info"]

    def __init__(self):
        super().__init__()
        self._adc_info = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "ADC", "CMD_ADC", result.name)
        self._adc_info = ADCInfo(data, offset)

    @property
    def adc_info(self):
        """
        The ADC information.
        """
        return self._adc_info
