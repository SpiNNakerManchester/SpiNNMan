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
    AbstractSCPRequest, BMPRequest, BMPResponse)
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.scp import SCPRequestHeader

_ONE_WORD = struct.Struct("<I")


class ReadFPGARegister(BMPRequest['_SCPReadFPGARegisterResponse']):
    """
    Requests the data from a FPGA's register.
    """
    __slots__ = ()

    def __init__(self, fpga_num: int, register: int, board: int):
        """
        Sets up a read FPGA register request.

        :param fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param register:
            Register address to read to (will be rounded down to
            the nearest 32-bit word boundary).
        :param board: which board to request the FPGA register from
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
    def get_scp_response(self) -> '_SCPReadFPGARegisterResponse':
        return _SCPReadFPGARegisterResponse(
            "Read FPGA register", SCPCommand.CMD_LINK_READ)


class _SCPReadFPGARegisterResponse(BMPResponse[int]):
    """
    An SCP response to a request for the version of software running.
    """
    def _parse_payload(self, data: bytes, offset: int) -> int:
        return _ONE_WORD.unpack_from(data, offset)[0]

    @property
    def fpga_register(self) -> int:
        """
        The register information received.
        """
        return self._value
