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
from spinnman.exceptions import (
    SpinnmanUnexpectedResponseCodeException, SpinnmanInvalidParameterException)

_ONE_WORD = struct.Struct("<I")


class SDRAMAlloc(AbstractSCPRequest):
    """ An SCP Request to allocate space in the SDRAM space
    """
    __slots__ = [
        "_size"]

    def __init__(self, x, y, app_id, size, tag=None):
        """
        :param x: \
            The x-coordinate of the chip to allocate on, between 0 and 255
        :type x: int
        :param y: \
            The y-coordinate of the chip to allocate on, between 0 and 255
        :type y: int
        :param app_id: The ID of the application, between 0 and 255
        :type app_id: int
        :param size: The size in bytes of memory to be allocated
        :type size: int
        :param tag: the tag for the SDRAM, a 8-bit (chip-wide) tag that can be\
            looked up by a SpiNNaker application to discover the address of\
            the allocated block. If `0` then no tag is applied.
        :type tag: int
        """
        # pylint: disable=too-many-arguments
        if tag is None:
            tag = 0
        elif not(0 <= tag < 256):
            raise SpinnmanInvalidParameterException(
                "tag",
                "The tag param needs to be between 0 and 255, or None (in "
                "which case 0 will be used by default)", str(tag))

        super(SDRAMAlloc, self).__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_ALLOC),
            argument_1=(
                (app_id << 8) |
                AllocFree.ALLOC_SDRAM.value),  # @UndefinedVariable
            argument_2=size, argument_3=tag)
        self._size = size

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPSDRAMAllocResponse(self._size)


class _SCPSDRAMAllocResponse(AbstractSCPResponse):
    """ An SCP response to a request to allocate space in SDRAM
    """
    __slots__ = [
        "_base_address",
        "_size"]

    def __init__(self, size):
        super(_SCPSDRAMAllocResponse, self).__init__()
        self._size = size
        self._base_address = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "SDRAM Allocation", "CMD_ALLOC", result.name)
        self._base_address = _ONE_WORD.unpack_from(data, offset)[0]

        # check that the base address is not null (0 in python case) as
        # this reflects a issue in the command on SpiNNaker side
        if self._base_address == 0:
            raise SpinnmanInvalidParameterException(
                "SDRAM Allocation response base address", self._base_address,
                "Could not allocate {} bytes of SDRAM".format(self._size))

    @property
    def base_address(self):
        """ The base address allocated, or 0 if none

        :rtype: int
        """
        return self._base_address
