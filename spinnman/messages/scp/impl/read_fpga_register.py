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

import struct
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse, BMPRequest, BMPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.scp import SCPRequestHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_ONE_WORD = struct.Struct("<I")


class ReadFPGARegister(BMPRequest):
    """
    Requests the data from a FPGA's register.
    """
    __slots__ = []

    def __init__(self, fpga_num, register, board):
        """
        Sets up a read FPGA register request.

        :param int fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param int register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param int board: which board to request the FPGA register from
        """
        # check to stop people asking for non-word aligned memory addresses
        # inverses all bits of a value, so is basically a inverse mask for the
        # value entered.
        arg1 = register & (~0x3)
        super().__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_LINK_READ),
            argument_1=arg1, argument_2=4, argument_3=fpga_num)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPReadFPGARegisterResponse()


class _SCPReadFPGARegisterResponse(BMPResponse):
    """
    An SCP response to a request for the version of software running.
    """
    __slots__ = [
        "_fpga_register"]

    def __init__(self):
        super().__init__()
        self._fpga_register = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Read FPGA register", "CMD_LINK_READ", result.name)

        self._fpga_register = _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def fpga_register(self):
        """
        The register information received.

        :rtype: int
        """
        return self._fpga_register
