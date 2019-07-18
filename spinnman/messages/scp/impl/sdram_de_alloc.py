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

import struct
from spinn_utilities.overrides import overrides
from spinnman.messages.scp import SCPRequestHeader
from spinnman.messages.scp.abstract_messages import (
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import AllocFree, SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

_ONE_WORD = struct.Struct("<I")


class SDRAMDeAlloc(AbstractSCPRequest):
    """ An SCP Request to free space in the SDRAM
    """
    __slots__ = [
        "_read_n_blocks_freed"]

    def __init__(self, x, y, app_id, base_address=None):
        """
        :param x: \
            The x-coordinate of the chip to allocate on, between 0 and 255
        :type x: int
        :param y: \
            The y-coordinate of the chip to allocate on, between 0 and 255
        :type y: int
        :param app_id: The ID of the application, between 0 and 255
        :type app_id: int
        :param base_address: The start address in SDRAM to which the block\
            needs to be deallocated, or none if deallocating via app_id
        :type base_address: int or None
        """

        if base_address is not None:
            super(SDRAMDeAlloc, self).__init__(
                SDPHeader(
                    flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
                argument_1=(
                    AllocFree.
                    FREE_SDRAM_BY_POINTER.value),  # @UndefinedVariable
                argument_2=base_address)
            self._read_n_blocks_freed = False
        else:
            super(SDRAMDeAlloc, self).__init__(
                SDPHeader(
                    flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                    destination_cpu=0, destination_chip_x=x,
                    destination_chip_y=y),
                SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
                argument_1=(
                    app_id << 8 |
                    AllocFree.
                    FREE_SDRAM_BY_APP_ID.value))  # @UndefinedVariable
            self._read_n_blocks_freed = True

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPSDRAMDeAllocResponse(self._read_n_blocks_freed)


class _SCPSDRAMDeAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to deallocate SDRAM
    """
    __slots__ = [
        "_number_of_blocks_freed",
        "_read_n_blocks_freed"]

    def __init__(self, read_n_blocks_freed=False):
        """
        """
        super(_SCPSDRAMDeAllocResponse, self).__init__()
        self._number_of_blocks_freed = None
        self._read_n_blocks_freed = read_n_blocks_freed

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM deallocation", "CMD_DEALLOC", result.name)
        if self._read_n_blocks_freed:
            self._number_of_blocks_freed = _ONE_WORD.unpack_from(
                data, offset)[0]

            # check that the base address is not null (0 in python case) as
            # this reflects a issue in command on SpiNNaker side
            if self._number_of_blocks_freed == 0:
                raise SpinnmanUnexpectedResponseCodeException(
                    "SDRAM deallocation response base address", "CMD_DEALLOC",
                    result.name)

    @property
    def number_of_blocks_freed(self):
        """ The number of allocated blocks that have been freed from the\
            app_id given

        :rtype: int
        """
        return self._number_of_blocks_freed
