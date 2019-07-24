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
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse, BMPRequest, BMPResponse)
from spinnman.messages.scp.enums import BMPInfo, SCPCommand, SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from spinnman.model import ADCInfo


class ReadADC(BMPRequest):
    """ SCP Request for the data from the BMP including voltages and\
        temperature.
    """
    __slots__ = []

    def __init__(self, board):
        """
        :param board: which board to request the ADC register from
        :rtype: None
        """
        super(ReadADC, self).__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_BMP_INFO),
            argument_1=BMPInfo.ADC)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPReadADCResponse()


class _SCPReadADCResponse(BMPResponse):
    """ An SCP response to a request for ADC information
    """
    __slots__ = [
        "_adc_info"]

    def __init__(self):
        super(_SCPReadADCResponse, self).__init__()
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
        """ The ADC information
        """
        return self._adc_info
