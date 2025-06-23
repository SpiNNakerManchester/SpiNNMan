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
from typing import Iterable, Optional
from spinn_utilities.overrides import overrides
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.messages.scp.impl.check_ok_response import CheckOKResponse


_WAIT_FLAG = 0x1 << 18


class AppCopyRun(AbstractSCPRequest[CheckOKResponse]):
    """
    An SCP request to copy an application and start it.
    """
    __slots__ = "__link",

    def __init__(self, x: int, y: int, link: int, size: int, app_id: int,
                 processors: Optional[Iterable[int]],
                 checksum: int, wait: bool = False):
        """
        :param x:
            The x-coordinate of the chip to read from, between 0 and 255
        :param y:
            The y-coordinate of the chip to read from, between 0 and 255
        :param link: The ID of the link from which to copy
        :param size: The number of bytes to read, must be divisible by 4
        :param app_id: The app to associate the copied binary with
        :param processors: The processors to start on the chip
        :param checksum: The checksum of the data to copy
        :param wait: Whether to start in wait mode or not
        """
        if size % 4 != 0:
            raise SpinnmanInvalidParameterException(
                "size", size, "The size must be a multiple of 4")

        processor_mask = 0
        if processors is not None:
            for processor in processors:
                processor_mask |= (1 << processor)

        processor_mask |= (app_id << 24)
        if wait:
            processor_mask |= _WAIT_FLAG
        self.__link = link

        arg1 = ((checksum & 0x1FFFFFFF) << 3) | link

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_APP_COPY_RUN),
            argument_1=arg1, argument_2=size, argument_3=processor_mask)

    def __repr__(self) -> str:
        return f"{super(AppCopyRun, self).__repr__()} (Link {self.__link})"

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self) -> CheckOKResponse:
        return CheckOKResponse(
            f"Application Copy Run (Link {self.__link})",
            SCPCommand.CMD_APP_COPY_RUN)
