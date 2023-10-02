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

import struct
from .sdp_flag import SDPFlag
from spinnman.data import SpiNNManDataView

N_BYTES = 8
_EIGHT_BYTES = struct.Struct("<8B")


class SDPHeader(object):
    """
    Represents the header of an SDP message.
    Each optional parameter in the constructor can be set to a value other
    than `None` once, after which it is immutable.  It is an error to set a
    parameter that is not currently `None`.
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
        :param SDPFlag flags: Any flags for the packet
        :param int tag:
            The IP tag of the packet between 0 and 255, or `None` if it
            is to be set later
        :param int destination_port:
            The destination port of the packet between 0 and 7
        :param int destination_cpu:
            The destination processor ID within the chip between 0 and 31
        :param int destination_chip_x:
            The x-coordinate of the destination chip between 0 and 255
        :param int destination_chip_y:
            The y-coordinate of the destination chip between 0 and 255
        :param int source_port:
            The source port of the packet between 0 and 7, or
            `None` if it is to be set later
        :param int source_cpu:
            The source processor ID within the chip between 0 and 31,
            or `None` if it is to be set later
        :param int source_chip_x:
            The x-coordinate of the source chip between 0 and 255,
            or `None` if it is to be set later
        :param int source_chip_y:
            The y-coordinate of the source chip between 0 and 255,
            or `None` if it is to be set later
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
        """
        The flags of the packet (settable).

        :rtype: SDPFlag
        """
        return self._flags

    @flags.setter
    def flags(self, flags):
        """
        Set the flags of the packet.

        :param SDPFlag flags: The flags to set
        """
        self._flags = flags

    @property
    def tag(self):
        """
        The tag of the packet, between 0 and 255 (settable).

        :rtype: int
        """
        return self._tag

    @tag.setter
    def tag(self, tag):
        """
        Set the tag of the packet.

        :param int tag: The tag to set, between 0 and 255
        """
        self._tag = tag

    @property
    def destination_port(self):
        """
        The destination SDP port of the packet, between 0 and 7 (settable).

        :rtype: int
        """
        return self._destination_port

    @destination_port.setter
    def destination_port(self, destination_port):
        """
        Set the destination port of the packet.

        :param int destination_port:
            The destination port to set, between 0 and 7
        """
        self._destination_port = destination_port

    @property
    def destination_cpu(self):
        """
        The core on the destination chip, between 0 and 31 (settable).

        :rtype: int
        """
        return self._destination_cpu

    @destination_cpu.setter
    def destination_cpu(self, destination_cpu):
        """
        Set the ID of the destination processor of the packet.

        :param int destination_cpu:
            The processor ID to set, between 0 and 31
        """
        self._destination_cpu = destination_cpu

    @property
    def destination_chip_x(self):
        """
        The x-coordinate of the destination chip of the packet, between
        0 and 255 (settable).

        :rtype: int
        """
        return self._destination_chip_x

    @destination_chip_x.setter
    def destination_chip_x(self, destination_chip_x):
        """
        Set the x-coordinate of the destination chip of the packet.

        :param int destination_chip_x:
            The x-coordinate to set, between 0 and 255
        """
        self._destination_chip_x = destination_chip_x

    @property
    def destination_chip_y(self):
        """
        The y-coordinate of the destination chip of the packet, between
        0 and 255 (settable).

        :rtype: int
        """
        return self._destination_chip_y

    @destination_chip_y.setter
    def destination_chip_y(self, destination_chip_y):
        """
        Set the y-coordinate of the destination chip of the packet.

        :param int destination_chip_y:
            The y-coordinate to set, between 0 and 255
        """
        self._destination_chip_y = destination_chip_y

    @property
    def source_port(self):
        """
        The source SDP port of the packet, between 0 and 7 (settable).

        :rtype: int
        """
        return self._source_port

    @source_port.setter
    def source_port(self, source_port):
        """
        Set the source port of the packet.

        :param int source_port: The source port to set, between 0 and 7
        """
        self._source_port = source_port

    @property
    def source_cpu(self):
        """
        The core on the source chip, between 0 and 31 (settable).

        :rtype: int
        """
        return self._source_cpu

    @source_cpu.setter
    def source_cpu(self, source_cpu):
        """
        Set the ID of the source processor of the packet.

        :param int source_cpu: The processor ID to set, between 0 and 31
        """
        self._source_cpu = source_cpu

    @property
    def source_chip_x(self):
        """
        The x-coordinate of the source chip of the packet, between
        0 and 255 (settable).

        :rtype: int
        """
        return self._source_chip_x

    @source_chip_x.setter
    def source_chip_x(self, source_chip_x):
        """
        Set the x-coordinate of the source chip of the packet.

        :param int source_chip_x:
            The x-coordinate to set, between 0 and 255
        """
        self._source_chip_x = source_chip_x

    @property
    def source_chip_y(self):
        """
        The y-coordinate of the source chip of the packet, between
        0 and 255 (settable).

        :rtype: int
        """
        return self._source_chip_y

    @source_chip_y.setter
    def source_chip_y(self, source_chip_y):
        """
        Set the y-coordinate of the source chip of the packet.

        :param int source_chip_y:
            The y-coordinate to set, between 0 and 255
        """
        self._source_chip_y = source_chip_y

    @property
    def bytestring(self):
        """
        The header as a byte-string.

        :rtype: bytes
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
        """
        Read the header from a byte-string.

        :param data: The byte-string to read the header from
        :type data: bytes or bytearray
        :param int offset:
            The offset into the data from which to start reading
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

    def get_physical_cpu_id(self):
        if SpiNNManDataView.has_machine():
            chip = SpiNNManDataView.get_machine().get_chip_at(
                self._destination_chip_x,  self._destination_chip_y)
            if chip is not None:
                return chip.get_physical_core_string(
                    self._destination_cpu)
        return ""
