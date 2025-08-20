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

from typing import List, Union
import struct

from spinn_utilities.overrides import overrides
from spinnman.exceptions import (
    SpinnmanInvalidPacketException, SpinnmanInvalidParameterTypeException)
from spinnman.constants import EIEIO_COMMAND_IDS

from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader

_PATTERN_BBBB = struct.Struct("<BBBB")
_PATTERN_BBII = struct.Struct("<BBII")
_PATTERN_xxBBII = struct.Struct("<xxBBII")
_PATTERN_BB = struct.Struct("<BB")
_PATTERN_BBBBII = struct.Struct("<BBBBII")


class SpinnakerRequestReadData(EIEIOCommandMessage):
    """
    Message used in the context of the buffering output mechanism which is
    sent from the SpiNNaker system to the host computer to signal that
    some data is available to be read.
    """
    __slots__ = (
        "_header",
        "_requests")

    def __init__(
            self, x: int, y: int, p: int, region_id: Union[List[int], int],
            sequence_no: int, n_requests: int, channel: Union[List[int], int],
            start_address: Union[List[int], int],
            space_to_be_read: Union[List[int], int]):
        """

        :param x:
        :param y:
        :param p:
        :param region_id:
        :param sequence_no:
        :param n_requests:
        :param channel:
        :param start_address:
        :param space_to_be_read:
        """
        if not isinstance(channel, list):
            channel = [channel]

        if not isinstance(region_id, list):
            region_id = [region_id]

        if not isinstance(start_address, list):
            start_address = [start_address]

        if not isinstance(space_to_be_read, list):
            space_to_be_read = [space_to_be_read]

        if len(start_address) != n_requests or \
                len(space_to_be_read) != n_requests or \
                len(channel) != n_requests or \
                len(region_id) != n_requests:
            raise SpinnmanInvalidPacketException(
                "SpinnakerRequestReadData",
                "The format for a SpinnakerRequestReadData packet is "
                f"invalid: {n_requests:d} request(s), "
                f"{len(start_address):d} start address(es) defined, "
                f"{len(space_to_be_read):d} space(s) to be read defined, "
                f"{len(region_id):d} region(s) defined, "
                f"{len(channel):d} channel(s) defined")

        super().__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.SPINNAKER_REQUEST_READ_DATA))
        self._header = _SpinnakerRequestReadDataHeader(
            x, y, p, n_requests, sequence_no)
        self._requests = _SpinnakerRequestReadDataRequest(
            channel, region_id, start_address, space_to_be_read)

    @property
    def x(self) -> int:
        """
        The x value passed into the init. """
        return self._header.x

    @property
    def y(self) -> int:
        """
        The y value passed into the init. """
        return self._header.y

    @property
    def p(self) -> int:
        """
        The p value passed into the init. """
        return self._header.p

    @property
    def n_requests(self) -> int:
        """
        The n_requests value passed into the init. """
        return self._header.n_requests

    @property
    def sequence_no(self) -> int:
        """
        The sequence_no value passed into the init. """
        return self._header.sequence_no

    def channel(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The channel for this request_id.
        :raises IndexError: If the request_id is invalid
        """
        return self._requests.channel(request_id)

    def region_id(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The region_id for this request_id.
        :raises IndexError: If the request_id is invalid
        """
        return self._requests.region_id(request_id)

    def start_address(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The start_address value for this request_id.
        :raises IndexError: If the request_id is invalid
        """
        return self._requests.start_address(request_id)

    def space_to_be_read(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The space_to_be_read for this request_id.
        :raises IndexError: If the request_id is invalid
        """
        return self._requests.space_to_be_read(request_id)

    @staticmethod
    @overrides(EIEIOCommandMessage.get_min_packet_length)
    def get_min_packet_length() -> int:
        return 16

    @staticmethod
    @overrides(EIEIOCommandMessage.from_bytestring)
    def from_bytestring(command_header: EIEIOCommandHeader, data: bytes,
                        offset: int) -> "SpinnakerRequestReadData":
        (y, x, processor_and_requests, sequence_no) = \
            _PATTERN_BBBB.unpack_from(data, offset)
        p = (processor_and_requests >> 3) & 0x1F
        n_requests = processor_and_requests & 0x7
        offset += 4
        channel = list()
        region_id = list()
        start_address = list()
        space_to_be_read = list()

        for i in range(n_requests):
            if i == 0:
                request_channel, request_region_id, request_start_address, \
                    request_space_to_be_read = _PATTERN_BBII.unpack_from(
                        data, offset)
                offset += 10
            else:
                request_channel, request_region_id, request_start_address, \
                    request_space_to_be_read = _PATTERN_xxBBII.unpack_from(
                        data, offset)
                offset += 12
            channel.append(request_channel)
            region_id.append(request_region_id)
            start_address.append(request_start_address)
            space_to_be_read.append(request_space_to_be_read)
        return SpinnakerRequestReadData(
            x, y, p, region_id, sequence_no, n_requests, channel,
            start_address, space_to_be_read)

    @property
    @overrides(EIEIOCommandMessage.bytestring)
    def bytestring(self) -> bytes:
        byte_string = super().bytestring
        byte_string += _PATTERN_BB.pack(self.x, self.y)
        n_requests = self.n_requests
        processor_and_request = (self.p << 3) | n_requests

        for i in range(n_requests):
            if i == 0:
                byte_string += _PATTERN_BBBBII.pack(
                    processor_and_request, self.sequence_no,
                    self.channel(i), self.region_id(i),
                    self.start_address(0), self.space_to_be_read(i))
            else:
                byte_string += _PATTERN_xxBBII.pack(
                    self.channel(i), self.region_id(i),
                    self.start_address(0), self.space_to_be_read(i))
        return byte_string


class _SpinnakerRequestReadDataHeader(object):
    """
    Contains the position of the core in the machine (x, y, p), the number
    of requests and a sequence number.
    """
    __slots__ = [
        "_n_requests",
        "_sequence_no",
        "_p", "_x", "_y"]

    def __init__(
            self, x: int, y: int, p: int, n_requests: int, sequence_no: int):
        """

        :param x:
        :param y:
        :param p:
        :param n_requests:
        :param sequence_no:
        """
        self._x = x
        self._y = y
        self._p = p
        self._n_requests = n_requests
        self._sequence_no = sequence_no

    @property
    def x(self) -> int:
        """
        The x value passed into the init."""
        return self._x

    @property
    def y(self) -> int:
        """
        The y value passed into the init. """
        return self._y

    @property
    def p(self) -> int:
        """
        The p value passed into the init. """
        return self._p

    @property
    def sequence_no(self) -> int:
        """
        The sequence_no value passed into the init. """
        return self._sequence_no

    @property
    def n_requests(self) -> int:
        """
        The n_request value passed into the init. """
        return self._n_requests


class _SpinnakerRequestReadDataRequest(object):
    """
    Contains a set of requests which refer to the channels used.
    """
    __slots__ = [
        "_channel",
        "_region_id",
        "_start_address",
        "_space_to_be_read"]

    def __init__(self, channel: Union[List[int], int],
                 region_id: Union[List[int], int],
                 start_address: Union[List[int], int],
                 space_to_be_read: Union[List[int], int]):
        """

        :param channel:
        :param region_id:
        :param start_address:
        :param space_to_be_read:
        """
        if not isinstance(channel, list):
            self._channel = [channel]
        else:
            self._channel = channel

        if not isinstance(region_id, list):
            self._region_id = [region_id]
        else:
            self._region_id = region_id

        if not isinstance(start_address, list):
            self._start_address = [start_address]
        else:
            self._start_address = start_address

        if not isinstance(space_to_be_read, list):
            self._space_to_be_read = [space_to_be_read]
        else:
            self._space_to_be_read = space_to_be_read

    def channel(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The channel for this request_id
        :raises SpinnmanInvalidParameterTypeException:
            if the request_id os too high
        """

        if len(self._channel) > request_id:
            return self._channel[request_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"channel request needs to be comprised between 0 and "
            f"{len(self._channel) - 1:d}; current value: {request_id:d}")

    def region_id(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The region_id for this request_id
        :raises SpinnmanInvalidParameterTypeException:
            if the request_id os too high
        """
        if len(self._region_id) > request_id:
            return self._region_id[request_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"region ID request needs to be comprised between 0 and "
            f"{len(self._region_id) - 1:d}; current value: {request_id:d}")

    def start_address(self, request_id: int) -> int:
        """
        :param request_id:
        :returns: The start address for this request_id
        :raises SpinnmanInvalidParameterTypeException:
            if the request_id os too high
        """
        if len(self._start_address) > request_id:
            return self._start_address[request_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"start address request needs to be comprised between 0 and "
            f"{len(self._start_address) - 1:d}; current value: {request_id:d}")

    def space_to_be_read(self, request_id: int) -> int:
        """
        Checks if there is enough space to request this id

        :returns: The space to read for this ID
        :raises SpinnmanInvalidParameterTypeException:
            if the request_id os too high
        """
        if len(self._space_to_be_read) > request_id:
            return self._space_to_be_read[request_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"space to be read request needs to be comprised between 0 and "
            f"{len(self._space_to_be_read) - 1:d}; "
            f"current value: {request_id:d}")
