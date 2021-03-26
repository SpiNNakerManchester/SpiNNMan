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
    AbstractSCPRequest, AbstractSCPResponse)
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.messages.sdp import SDPFlag, SDPHeader
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException

import struct


_IPTAG_GET = 2

_IPTAG_FORMAT = struct.Struct("<4s6s3HIH3B")


class IPTagGet(AbstractSCPRequest):
    """ An SCP Request to get an IP tag
    """
    __slots__ = []

    def __init__(self, x, y, tag):
        """
        :param int x: The x-coordinate of a chip, between 0 and 255
        :param int y: The y-coordinate of a chip, between 0 and 255
        :param int tag: The tag to get details of, between 0 and 7
        :param int tag: The tag, between 0 and 7
        """
        super().__init__(
            SDPHeader(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=0,
                destination_cpu=0, destination_chip_x=x,
                destination_chip_y=y),
            SCPRequestHeader(command=SCPCommand.CMD_IPTAG),
            argument_1=(_IPTAG_GET << 16) | tag,
            argument_2=1)

    @overrides(AbstractSCPRequest.get_scp_response)
    def get_scp_response(self):
        return _SCPIPTagGetResponse()


class _SCPIPTagGetResponse(AbstractSCPResponse):
    """ An SCP response to a request for an IP tags
    """
    __slots__ = [
        "_count",
        "_flags",
        "_ip_address",
        "_mac_address",
        "_port",
        "_rx_port",
        "_spin_chip_x",
        "_spin_chip_y",
        "_spin_cpu",
        "_spin_port",
        "_timeout"]

    def __init__(self):
        """
        """
        super().__init__()
        self._ip_address = None
        self._mac_address = None
        self._port = None
        self._timeout = None
        self._flags = None
        self._count = None
        self._rx_port = None
        self._spin_chip_y = None
        self._spin_chip_x = None
        self._spin_cpu = None
        self._spin_port = None

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data, offset):
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                "Get IP Tag Info", "CMD_IPTAG", result.name)
        (ip_address, mac_address, self._port, self._timeout,
         self._flags, self._count, self._rx_port, self._spin_chip_y,
         self._spin_chip_x, processor_and_port) = _IPTAG_FORMAT.unpack_from(
            data, offset)
        self._ip_address = bytearray(ip_address)
        self._mac_address = bytearray(mac_address)
        self._spin_port = (processor_and_port >> 5) & 0x7
        self._spin_cpu = processor_and_port & 0x1F

    @property
    def ip_address(self):
        """ The IP address of the tag, as a bytearray of 4 bytes

        :rtype: bytearray
        """
        return self._ip_address

    @property
    def mac_address(self):
        """ The MAC address of the tag, as a bytearray of 6 bytes

        :rtype: bytearray
        """
        return self._mac_address

    @property
    def port(self):
        """ The port of the tag

        :rtype: int
        """
        return self._port

    @property
    def timeout(self):
        """ The timeout of the tag

        :rtype: int
        """
        return self._timeout

    @property
    def flags(self):
        """ The flags of the tag

        :rtype: int
        """
        return self._flags

    @property
    def in_use(self):
        """ True if the tag is marked as being in use

        :rtype: bool
        """
        return (self._flags & 0x8000) > 0

    @property
    def is_temporary(self):
        """ True if the tag is temporary

        :rtype: bool
        """
        return (self._flags & 0x4000) > 0

    @property
    def is_arp(self):
        """ True if the tag is in the ARP state (where the MAC address is\
            being looked up - transient state so unlikely)

        :rtype: bool
        """
        return (self._flags & 0x2000) > 0

    @property
    def is_reverse(self):
        """ True if the tag is a reverse tag

        :rtype: bool
        """
        return (self._flags & 0x0200) > 0

    @property
    def strip_sdp(self):
        """ True if the tag is to strip the SDP header

        :rtype: bool
        """
        return (self._flags & 0x0100) > 0

    @property
    def count(self):
        """ The count of the number of packets that have been sent with the tag

        :rtype: int
        """
        return self._count

    @property
    def rx_port(self):
        """ The receive port of the tag

        :rtype: int
        """
        return self._rx_port

    @property
    def spin_chip_x(self):
        """ The x-coordinate of the chip on which the tag is defined

        :rtype: int
        """
        return self._spin_chip_x

    @property
    def spin_chip_y(self):
        """ The y-coordinate of the chip on which the tag is defined

        :rtype: int
        """
        return self._spin_chip_y

    @property
    def spin_port(self):
        """ The spin-port of the IP tag

        :rtype: int
        """
        return self._spin_port

    @property
    def spin_cpu(self):
        """ The CPU ID of the IP tag

        :rtype: int
        """
        return self._spin_cpu
