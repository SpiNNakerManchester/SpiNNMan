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
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums import SCPCommand
from spinnman.messages.sdp import SDPFlag, SDPHeader
from .check_ok_response import CheckOKResponse


class RouterInit(AbstractSCPRequest):
    """
    A request to initialize the router on a chip.
    """
    __slots__ = []

    def __init__(self, x, y, n_entries, table_address, base_address, app_id):
        """
        :param int x: The x-coordinate of the chip, between 0 and 255
        :param int y: The y-coordinate of the chip, between 0 and 255
        :param int n_entries: The number of entries in the table, more than 0
        :param int table_address: The allocated table address
        :param int base_address: The base_address containing the entries
        :param int app_id:
            The ID of the application with which to associate the
            routes.  If not specified, defaults to 0.
        :raise SpinnmanInvalidParameterException:
            * If x is out of range
            * If y is out of range
            * If n_entries is 0 or less
            * If table_address is not positive
            * If base_address is not positive
        """
        # pylint: disable=too-many-arguments
        if n_entries < 1:
            raise SpinnmanInvalidParameterException(
                "n_entries", str(n_entries), "Must be more than 0")
        if base_address < 0:
            raise SpinnmanInvalidParameterException(
                "base_address", str(base_address),
                "Must be a positive integer")
        if table_address < 0:
            raise SpinnmanInvalidParameterException(
                "table_address", str(table_address),
                "Must be a positive integer")

        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_RTR),
            argument_1=((n_entries << 16) | (app_id << 8) | 2),
            argument_2=table_address, argument_3=base_address)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return CheckOKResponse("RouterInit", "CMD_RTR")
