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
    AbstractSCPRequest, BMPRequest)
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.enums import SCPCommand
from .check_ok_response import CheckOKResponse

_ONE_WORD = struct.Struct("<I")


class WriteFPGARegister(BMPRequest):
    """
    A request for writing a word to a FPGA (SPI) register.

    See the SpI/O project's spinnaker_fpga design's `README`_ for a listing
    of FPGA registers. The SpI/O project can be found on GitHub at:
    https://github.com/SpiNNakerManchester/spio/

    .. _README: https://github.com/SpiNNakerManchester/spio/\
                blob/master/designs/spinnaker_fpgas/README.md#spi-interface
    """
    __slots__ = []

    def __init__(self, fpga_num, addr, value, board):
        """
        :param int fpga_num: FPGA number (0, 1 or 2) to communicate with.
        :param int addr: Register address to read or write to (will be rounded
            down to the nearest 32-bit word boundary).
        :param int value: A 32-bit int value to write to the register
        """
        super().__init__(
            board,
            SCPRequestHeader(command=SCPCommand.CMD_LINK_WRITE),
            argument_1=addr & (~0x3), argument_2=4, argument_3=fpga_num,
            data=_ONE_WORD.pack(value))

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("Send FPGA register write", "CMD_LINK_WRITE")
