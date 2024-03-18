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

import struct
from typing import List, Union

from spinn_utilities.overrides import overrides
from spinnman.exceptions import (
    SpinnmanInvalidPacketException, SpinnmanInvalidParameterTypeException)
from spinnman.constants import EIEIO_COMMAND_IDS

from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader

_PATTERN_BB = struct.Struct("<BB")
_PATTERN_xxBBI = struct.Struct("<xxBBI")


class HostDataRead(EIEIOCommandMessage):
    """
    Packet sent by the host computer to the SpiNNaker system in the
    context of the buffering output technique to signal that the host has
    completed reading data from the output buffer, and that such space can
    be considered free to use again.
    """
    __slots__ = (
        "_acks",
        "_header")

    def __init__(
            self, n_requests: int, sequence_no: int,
            channel: Union[List[int], int], region_id: Union[List[int], int],
            space_read: Union[List[int], int]):
        """

        :param int n_requests:
        :param int sequence_no:
        :param channel:
        :type channel: list(int) or int
        :param region_id:
        :type region_id: list(int) or int
        :param space_read:
        :type space_read: list(int) or int
        """
        # pylint: disable=too-many-arguments
        if not isinstance(channel, list):
            channel = [channel]

        if not isinstance(region_id, list):
            region_id = [region_id]

        if not isinstance(space_read, list):
            space_read = [space_read]

        if len(channel) != n_requests or \
                len(region_id) != n_requests or \
                len(space_read) != n_requests:
            raise SpinnmanInvalidPacketException(
                "SpinnakerRequestReadData",
                "The format for a SpinnakerRequestReadData packet is "
                f"invalid: {n_requests} request(s), {len(space_read)} "
                f"space(s) read defined, {len(region_id)} region(s) defined, "
                f"{len(channel)} channel(s) defined")
        super().__init__(EIEIOCommandHeader(EIEIO_COMMAND_IDS.HOST_DATA_READ))
        self._header = _HostDataReadHeader(n_requests, sequence_no)
        self._acks = _HostDataReadAck(channel, region_id, space_read)

    @property
    def n_requests(self) -> int:
        """
        Gets the n_requests passed into the init.

        :rtype: int
        """
        return self._header.n_requests

    @property
    def sequence_no(self) -> int:
        """
        Gets the sequence_no passed into the init.

        :rtype: int
        """
        return self._header.sequence_no

    def channel(self, ack_id: int) -> int:
        """
        Gets the channel value for this ack_id.

        :param int ack_id:
        :rtype: int
        :raises SpinnmanInvalidParameterTypeException:
            If the ack_id is invalid
        """
        return self._acks.channel(ack_id)

    def region_id(self, ack_id: int) -> int:
        """
        Gets the region_id value for this ack_id.

        :param int ack_id:
        :rtype: int
        :raises SpinnmanInvalidParameterTypeException:
            If the ack_id is invalid
        """
        return self._acks.region_id(ack_id)

    def space_read(self, ack_id: int) -> int:
        """
        Gets the space_read value for this ack_id.

        :param int ack_id:
        :rtype: int
        :raises SpinnmanInvalidParameterTypeException:
            If the ack_id is invalid
        """
        return self._acks.space_read(ack_id)

    @staticmethod
    @overrides(EIEIOCommandMessage.get_min_packet_length)
    def get_min_packet_length() -> int:
        return 8

    @staticmethod
    @overrides(EIEIOCommandMessage.from_bytestring)
    def from_bytestring(command_header: EIEIOCommandHeader, data: bytes,
                        offset: int) -> "HostDataRead":
        n_requests, sequence_no = _PATTERN_BB.unpack_from(data, offset)

        offset += 2
        n_requests &= 0x7
        channel = list()
        region_id = list()
        space_read = list()

        for _ in range(n_requests):
            channel_ack, region_id_ack, space_read_ack = \
                _PATTERN_xxBBI.unpack_from(data, offset)
            channel.append(channel_ack)
            region_id.append(region_id_ack)
            space_read.append(space_read_ack)
            offset += 8
        return HostDataRead(
            n_requests, sequence_no, channel, region_id, space_read)

    @property
    @overrides(EIEIOCommandMessage.bytestring)
    def bytestring(self) -> bytes:
        byte_string = super().bytestring
        n_requests = self.n_requests
        byte_string += _PATTERN_BB.pack(n_requests, self.sequence_no)
        for i in range(n_requests):
            byte_string += _PATTERN_xxBBI.pack(
                self.channel(i), self.region_id(i), self.space_read(i))
        return byte_string


class _HostDataReadHeader(object):
    """
    The HostDataRead contains itself on header with the number of requests
    and a sequence number.
    """
    __slots__ = [
        "_n_requests",
        "_sequence_no"]

    def __init__(self, n_requests: int, sequence_no: int):
        """

        :param int n_requests:
        :param int sequence_no:
        """
        self._n_requests = n_requests
        self._sequence_no = sequence_no

    @property
    def sequence_no(self) -> int:
        """
        Gets the sequence_no passed into the init.

        :rtype: int
        """
        return self._sequence_no

    @property
    def n_requests(self) -> int:
        """
        Gets the n_requests passed into the init.

        :rtype: int
        """
        return self._n_requests


class _HostDataReadAck(object):
    """
    Contains a set of ACKs which refer to each of the channels read.
    """
    __slots__ = [
        "_channel",
        "_region_id",
        "_space_read"]

    def __init__(self, channel: Union[List[int], int],
                 region_id: Union[List[int], int],
                 space_read: Union[List[int], int]):
        """

        :param channel:
        :type channel: list(int) or int
        :param region_id:
        :type region_id: list(int) or int
        :param space_read:
        :type space_read: list(int) or int
        """
        if not isinstance(channel, list):
            self._channel = [channel]
        else:
            self._channel = channel

        if not isinstance(region_id, list):
            self._region_id = [region_id]
        else:
            self._region_id = region_id

        if not isinstance(space_read, list):
            self._space_read = [space_read]
        else:
            self._space_read = space_read

    def channel(self, ack_id: int) -> int:
        """
        Gets the channel value for this ack_id.

        :param int ack_id:
        :rtype: int
        :raises SpinnmanInvalidParameterTypeException:
            If the ack_id is invalid
        """
        if len(self._channel) > ack_id:
            return self._channel[ack_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"channel ack_id needs to be comprised between 0 and "
            f"{len(self._channel) - 1:d}; current value: {ack_id:d}")

    def region_id(self, ack_id: int) -> int:
        """
        Gets the region_id value for this ack_id.

        :param int ack_id:
        :rtype: int
        :raises SpinnmanInvalidParameterTypeException:
            If the ack_id is invalid
        """
        if len(self._region_id) > ack_id:
            return self._region_id[ack_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"region ID ack_id needs to be comprised between 0 and "
            f"{len(self._region_id) - 1:d}; current value: {ack_id:d}")

    def space_read(self, ack_id: int) -> int:
        """
        Gets the space_read value for this ack_id.

        :param int ack_id:
        :rtype: int
        :raises SpinnmanInvalidParameterTypeException:
            If the ack_id is invalid
        """
        if len(self._space_read) > ack_id:
            return self._space_read[ack_id]
        raise SpinnmanInvalidParameterTypeException(
            "request_id", "integer",
            f"start address ack_id needs to be comprised between 0 and "
            f"{len(self._space_read) - 1:d}; current value: {ack_id:d}")
