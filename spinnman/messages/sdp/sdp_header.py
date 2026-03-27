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
from typing import Optional
from spinnman.data import SpiNNManDataView
from .sdp_flag import SDPFlag

N_BYTES = 8
_EIGHT_BYTES = struct.Struct("<8B")
_SDP_SOURCE_PORT = 7
_SDP_SOURCE_CPU = 31
_SDP_TAG = 0xFF


class SDPHeader(object):
    """
    Represents the header of an SDP message.
    Each optional parameter in the constructor can be set to a value other
    than `None` once, after which it is immutable.  It is an error to set a
    parameter that is not currently `None`.
    """
    __slots__ = (
        "_destination_chip_x",
        "_destination_chip_y",
        "_destination_cpu",
        "_destination_port",
        "_flags",
        "_source_chip_x",
        "_source_chip_y",
        "_source_cpu",
        "_source_port",
        "_tag")

    def __init__(self, flags: SDPFlag, tag: Optional[int] = None,
                 destination_port: int = 0, destination_cpu: int = 0,
                 destination_chip_x: int = 0, destination_chip_y: int = 0,
                 source_port: Optional[int] = None,
                 source_cpu: Optional[int] = None,
                 source_chip_x: Optional[int] = None,
                 source_chip_y: Optional[int] = None):
        """
        :param flags: Any flags for the packet
        :param tag:
            The IP tag of the packet between 0 and 255, or `None` if it
            is to be set later
        :param destination_port:
            The destination port of the packet between 0 and 7
        :param destination_cpu:
            The destination processor ID within the chip between 0 and 31
        :param destination_chip_x:
            The x-coordinate of the destination chip between 0 and 255
        :param destination_chip_y:
            The y-coordinate of the destination chip between 0 and 255
        :param source_port:
            The source port of the packet between 0 and 7, or
            `None` if it is to be set later
        :param source_cpu:
            The source processor ID within the chip between 0 and 31,
            or `None` if it is to be set later
        :param source_chip_x:
            The x-coordinate of the source chip between 0 and 255,
            or `None` if it is to be set later
        :param source_chip_y:
            The y-coordinate of the source chip between 0 and 255,
            or `None` if it is to be set later
        """
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
    def flags(self) -> SDPFlag:
        """
        The flags of the packet (settable).
        """
        return self._flags

    @flags.setter
    def flags(self, flags: SDPFlag) -> None:
        """
        Set the flags of the packet.

        :param flags: The flags to set
        """
        self._flags = flags

    @property
    def tag(self) -> int:
        """
        The tag of the packet, between 0 and 255 (settable).
        """
        assert self._tag is not None, "header not yet updated for send"
        return self._tag

    @tag.setter
    def tag(self, tag: int) -> None:
        """
        Set the tag of the packet.

        :param tag: The tag to set, between 0 and 255
        """
        self._tag = tag

    @property
    def destination_port(self) -> int:
        """
        The destination SDP port of the packet, between 0 and 7 (settable).
        """
        return self._destination_port

    @destination_port.setter
    def destination_port(self, destination_port: int) -> None:
        """
        Set the destination port of the packet.

        :param destination_port:
            The destination port to set, between 0 and 7
        """
        self._destination_port = destination_port

    @property
    def destination_cpu(self) -> int:
        """
        The core on the destination chip, between 0 and 31 (settable).
        """
        return self._destination_cpu

    @destination_cpu.setter
    def destination_cpu(self, destination_cpu: int) -> None:
        """
        Set the ID of the destination processor of the packet.

        :param destination_cpu:
            The processor ID to set, between 0 and 31
        """
        self._destination_cpu = destination_cpu

    @property
    def destination_chip_x(self) -> int:
        """
        The x-coordinate of the destination chip of the packet, between
        0 and 255 (settable).
        """
        return self._destination_chip_x

    @destination_chip_x.setter
    def destination_chip_x(self, destination_chip_x: int) -> None:
        """
        Set the x-coordinate of the destination chip of the packet.

        :param destination_chip_x:
            The x-coordinate to set, between 0 and 255
        """
        self._destination_chip_x = destination_chip_x

    @property
    def destination_chip_y(self) -> int:
        """
        The y-coordinate of the destination chip of the packet, between
        0 and 255 (settable).
        """
        return self._destination_chip_y

    @destination_chip_y.setter
    def destination_chip_y(self, destination_chip_y: int) -> None:
        """
        Set the y-coordinate of the destination chip of the packet.

        :param destination_chip_y:
            The y-coordinate to set, between 0 and 255
        """
        self._destination_chip_y = destination_chip_y

    @property
    def source_port(self) -> int:
        """
        The source SDP port of the packet, between 0 and 7 (settable).
        """
        assert self._source_port is not None, "header not yet updated for send"
        return self._source_port

    @source_port.setter
    def source_port(self, source_port: int) -> None:
        """
        Set the source port of the packet.

        :param source_port: The source port to set, between 0 and 7
        """
        self._source_port = source_port

    @property
    def source_cpu(self) -> int:
        """
        The core on the source chip, between 0 and 31 (settable).
        """
        assert self._source_cpu is not None, "header not yet updated for send"
        return self._source_cpu

    @source_cpu.setter
    def source_cpu(self, source_cpu: int) -> None:
        """
        Set the ID of the source processor of the packet.

        :param source_cpu: The processor ID to set, between 0 and 31
        """
        self._source_cpu = source_cpu

    @property
    def source_chip_x(self) -> int:
        """
        The x-coordinate of the source chip of the packet, between
        0 and 255 (settable).
        """
        assert self._source_chip_x is not None, \
            "header not yet updated for send"
        return self._source_chip_x

    @source_chip_x.setter
    def source_chip_x(self, source_chip_x: int) -> None:
        """
        Set the x-coordinate of the source chip of the packet.

        :param source_chip_x:
            The x-coordinate to set, between 0 and 255
        """
        self._source_chip_x = source_chip_x

    @property
    def source_chip_y(self) -> int:
        """
        The y-coordinate of the source chip of the packet, between
        0 and 255 (settable).
        """
        assert self._source_chip_y is not None, \
            "header not yet updated for send"
        return self._source_chip_y

    @source_chip_y.setter
    def source_chip_y(self, source_chip_y: int) -> None:
        """
        Set the y-coordinate of the source chip of the packet.

        :param source_chip_y:
            The y-coordinate to set, between 0 and 255
        """
        self._source_chip_y = source_chip_y

    @property
    def bytestring(self) -> bytes:
        """
        The header as a byte-string.
        """
        dest_port_cpu = (((self._destination_port & 0x7) << 5) |
                         (self._destination_cpu & 0x1F))
        source_port_cpu = (((self.source_port & 0x7) << 5) |
                           (self.source_cpu & 0x1F))

        return _EIGHT_BYTES.pack(
            self._flags.value, self.tag, dest_port_cpu, source_port_cpu,
            self._destination_chip_y, self._destination_chip_x,
            self.source_chip_y, self.source_chip_x)

    @staticmethod
    def from_bytestring(data: bytes, offset: int) -> "SDPHeader":
        """
        :param data: The byte-string to read the header from
        :param offset:
            The offset into the data from which to start reading
        :returns: The header from the byte-string.
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

    def get_physical_cpu_id(self) -> str:
        """
        A String describing the physical core of the destination.

        :return: A report / debug representation of the destination
        """
        return SpiNNManDataView.get_physical_string(
            (self._destination_chip_x, self._destination_chip_y),
            self._destination_cpu)

    def update_for_send(self, source_x: int, source_y: int) -> None:
        """
        Apply defaults to the header for sending over UDP.

        :param source_x:
            Where the packet is deemed to originate: X coordinate
        :param source_y:
            Where the packet is deemed to originate: Y coordinate
        """
        self.tag = _SDP_TAG
        self.source_port = _SDP_SOURCE_PORT
        self.source_cpu = _SDP_SOURCE_CPU
        self.source_chip_x = source_x
        self.source_chip_y = source_y
