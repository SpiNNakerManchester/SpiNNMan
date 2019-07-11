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
from .sdp_flag import SDPFlag

N_BYTES = 8
_EIGHT_BYTES = struct.Struct("<8B")


class SDPHeader(object):
    """ Represents the header of an SDP message.
        Each optional parameter in the constructor can be set to a value other\
        than None once, after which it is immutable.  It is an error to set a\
        parameter that is not currently None.
    """
    __slots__ = [
        "_destination_chip_x",
        "_destination_chip_y",
        "_destination_cpu",
        "_destination_port",
        "_flags",
        "_source_chip_x",
        "_source_chip_y",
        "_source_cpu",
        "_source_port",
        "_tag"]

    def __init__(self, flags=None, tag=None,
                 destination_port=None, destination_cpu=None,
                 destination_chip_x=None, destination_chip_y=None,
                 source_port=None, source_cpu=None,
                 source_chip_x=None, source_chip_y=None):
        """
        :param flags: Any flags for the packet
        :type flags: :py:class:`spinnman.messages.sdp.sdp_flag.SDPFlag`
        :param tag: The IP tag of the packet between 0 and 255, or None if it\
            is to be set later
        :type tag: int
        :param destination_port: \
            The destination port of the packet between 0 and 7
        :type destination_port: int
        :param destination_cpu: \
            The destination processor ID within the chip between 0 and 31
        :type destination_cpu: int
        :param destination_chip_x: \
            The x-coordinate of the destination chip between 0 and 255
        :type destination_chip_x: int
        :param destination_chip_y: \
            The y-coordinate of the destination chip between 0 and 255
        :type destination_chip_y: int
        :param source_port: The source port of the packet between 0 and 7, or\
            None if it is to be set later
        :type source_port: int
        :param source_cpu: The source processor ID within the chip between 0\
            and 31, or None if it is to be set later
        :type source_cpu: int
        :param source_chip_x: The x-coordinate of the source chip between 0\
            and 255, or None if it is to be set later
        :type source_chip_x: int
        :param source_chip_y: The y-coordinate of the source chip between 0\
            and 255, or None if it is to be set later
        """
        # pylint: disable=too-many-arguments
        self._flags = flags
        self._tag = tag
        self._destination_port = destination_port
        self._destination_cpu = destination_cpu
        self._destination_chip_x = destination_chip_x
        self._destination_chip_y = destination_chip_y
        self._source_port = source_port
        self._source_cpu = source_cpu
        self._source_chip_x = source_chip_x
        self._source_chip_y = source_chip_y

    @property
    def flags(self):
        """ The flags of the packet

        :return: The flags of the packet
        :rtype: :py:class:`spinnman.messages.sdp.sdp_flag.SDPFlag`
        """
        return self._flags

    @flags.setter
    def flags(self, flags):
        """ Set the flags of the packet

        :param flags: The flags to set
        :type flags: :py:class:`spinnman.messages.sdp.sdp_flag.SDPFlag`
        """
        self._flags = flags

    @property
    def tag(self):
        """ The tag of the packet

        :return: The tag of the packet between 0 and 255
        :rtype: int
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """ Set the tag of the packet

        :param tag: The tag to set, between 0 and 255
        :type tag: int
        """
        self._tag = tag

    @property
    def destination_port(self):
        """ The destination port of the packet

        :return: The destination port of the packet between 0 and 7
        :rtype: int
        """
        return self._destination_port

    @destination_port.setter
    def destination_port(self, destination_port):
        """ Set the destination port of the packet

        :param destination_port: The destination port to set, between 0 and 7
        :type destination_port: int
        """
        self._destination_port = destination_port

    @property
    def destination_cpu(self):
        """ The core on the destination chip

        :return: The core on the destination chip, between 0 and 31
        :rtype: int
        """
        return self._destination_cpu

    @destination_cpu.setter
    def destination_cpu(self, destination_cpu):
        """ Set the ID of the destination processor of the packet

        :param destination_cpu: The processor ID to set, between 0 and 31
        :type destination_cpu: int
        """
        self._destination_cpu = destination_cpu

    @property
    def destination_chip_x(self):
        """ The x-coordinate of the destination chip of the packet

        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._destination_chip_x

    @destination_chip_x.setter
    def destination_chip_x(self, destination_chip_x):
        """ Set the x-coordinate of the destination chip of the packet

        :param destination_chip_x: The x-coordinate to set, between 0 and 255
        :type destination_chip_x: int
        """
        self._destination_chip_x = destination_chip_x

    @property
    def destination_chip_y(self):
        """ The y-coordinate of the destination chip of the packet

        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._destination_chip_y

    @destination_chip_y.setter
    def destination_chip_y(self, destination_chip_y):
        """ Set the y-coordinate of the destination chip of the packet

        :param destination_chip_y: The y-coordinate to set, between 0 and 255
        :type destination_chip_y: int
        """
        self._destination_chip_y = destination_chip_y

    @property
    def source_port(self):
        """ The source port of the packet

        :return: The source port of the packet between 0 and 7
        :rtype: int
        """
        return self._source_port

    @source_port.setter
    def source_port(self, source_port):
        """ Set the source port of the packet

        :param source_port: The source port to set, between 0 and 7
        :type source_port: int
        """
        self._source_port = source_port

    @property
    def source_cpu(self):
        """ The core on the source chip

        :return: The core on the source chip, between 0 and 31
        :rtype: int
        """
        return self._source_cpu

    @source_cpu.setter
    def source_cpu(self, source_cpu):
        """ Set the ID of the source processor of the packet

        :param source_cpu: The processor ID to set, between 0 and 31
        :type source_cpu: int
        """
        self._source_cpu = source_cpu

    @property
    def source_chip_x(self):
        """ The x-coordinate of the source chip of the packet

        :return: The x-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._source_chip_x

    @source_chip_x.setter
    def source_chip_x(self, source_chip_x):
        """ Set the x-coordinate of the source chip of the packet

        :param source_chip_x: The x-coordinate to set, between 0 and 255
        :type source_chip_x: int
        """
        self._source_chip_x = source_chip_x

    @property
    def source_chip_y(self):
        """ The y-coordinate of the source chip of the packet

        :return: The y-coordinate of the chip, between 0 and 255
        :rtype: int
        """
        return self._source_chip_y

    @source_chip_y.setter
    def source_chip_y(self, source_chip_y):
        """ Set the y-coordinate of the source chip of the packet

        :param source_chip_y: The y-coordinate to set, between 0 and 255
        :type source_chip_y: int
        """
        self._source_chip_y = source_chip_y

    @property
    def bytestring(self):
        """ The header as a bytestring

        :return: The header bytestring
        :rtype: str
        """
        dest_port_cpu = (((self._destination_port & 0x7) << 5) |
                         (self._destination_cpu & 0x1F))
        source_port_cpu = (((self._source_port & 0x7) << 5) |
                           (self._source_cpu & 0x1F))

        return _EIGHT_BYTES.pack(
            self._flags.value, self._tag, dest_port_cpu, source_port_cpu,
            self._destination_chip_y, self._destination_chip_x,
            self._source_chip_y, self._source_chip_x)

    @staticmethod
    def from_bytestring(data, offset):
        """ Read the header from a bytestring

        :param data: The bytestring to read the header from
        :type data: str
        :param offset: The offset into the data from which to start reading
        :type offset: int
        """

        (flags, tag, dest_port_cpu, source_port_cpu,
         destination_chip_y, destination_chip_x,
         source_chip_y, source_chip_x) = _EIGHT_BYTES.unpack_from(data, offset)
        destination_port = dest_port_cpu >> 5
        destination_cpu = dest_port_cpu & 0x1F
        source_port = source_port_cpu >> 5
        source_cpu = source_port_cpu & 0x1F
        return SDPHeader(
            SDPFlag(flags), tag, destination_port, destination_cpu,
            destination_chip_x, destination_chip_y, source_port, source_cpu,
            source_chip_x, source_chip_y)
