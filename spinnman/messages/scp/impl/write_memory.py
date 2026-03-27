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

from spinn_utilities.overrides import overrides
from spinn_utilities.typing.coords import XYP
from spinnman.constants import address_length_dtype
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class WriteMemory(AbstractSCPRequest[CheckOKResponse]):
    """
    A request to write memory on a chip.
    """
    __slots__ = "_data_to_write",

    def __init__(self, coordinates: XYP, base_address: int, data: bytes):
        """
        :param coordinates:
            The coordinates of the chip, X and Y between 0 and 255, and P
            between 0 and 17 (normally 0 when writing to SDRAM; may be other
            values when writing to ITCM or DTCM);
            these are not checked due to speed restrictions
        :param base_address: The base_address to start writing to
            the base address is not checked to see if its not valid
        :param data: between 1 and 256 bytes of data to write;
            this is not checked due to speed restrictions
        """
        size = len(data)
        x, y, cpu = coordinates
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=cpu, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_WRITE),
            argument_1=base_address, argument_2=size,
            argument_3=address_length_dtype[
                (base_address % 4), (size % 4)].value,
            data=None)
        self._data_to_write = data

    @property
    def bytestring(self) -> bytes:
        return super().bytestring + bytes(self._data_to_write)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> CheckOKResponse:
        return CheckOKResponse("write to memory", "CMD_WRITE")
