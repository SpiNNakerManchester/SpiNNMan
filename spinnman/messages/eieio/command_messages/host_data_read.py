from spinnman.exceptions import SpinnmanInvalidPacketException, \
    SpinnmanInvalidParameterTypeException
from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS
import struct


class HostDataRead(EIEIOCommandMessage):
    """ Packet sent by the host computer to the SpiNNaker system in the\
        context of the buffering output technique to signal that the host has\
        completed reading data from the output buffer, and that such space can\
        be considered free to use again
    """
    def __init__(
            self, n_requests, sequence_no, channel, region_id, space_read):
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
                "invalid: {0:d} request(s), {1:d} space(s) read "
                "defined, {2:d} region(s) defined, {3:d} channel(s) "
                "defined".format(
                    n_requests, len(space_read), len(region_id), len(channel)))
        cmd_header = EIEIOCommandHeader(EIEIO_COMMAND_IDS.HOST_DATA_READ.value)
        EIEIOCommandMessage.__init__(self, cmd_header)
        self._header = _HostDataReadHeader(n_requests, sequence_no)
        self._acks = _HostDataReadAck(channel, region_id, space_read)

    @property
    def n_requests(self):
        return self._header.n_requests

    @property
    def sequence_no(self):
        return self._header.sequence_no

    def channel(self, ack_id):
        return self._acks.channel(ack_id)

    def region_id(self, ack_id):
        return self._acks.region_id(ack_id)

    def space_read(self, ack_id):
        return self._acks.space_read(ack_id)

    @staticmethod
    def get_min_packet_length():
        return 8

    @staticmethod
    def from_bytestring(command_header, data, offset):
        n_requests, sequence_no = struct.unpack_from(
            "<BB", data, offset)

        offset += 2
        n_requests &= 0x7
        channel = list()
        region_id = list()
        space_read = list()

        for _ in xrange(n_requests):
            channel_ack, region_id_ack, space_read_ack = \
                struct.unpack_from("<xxBBI", data, offset)
            channel.append(channel_ack)
            region_id.append(region_id_ack)
            space_read.append(space_read_ack)
            offset += 8
        return HostDataRead(
            n_requests, sequence_no, channel, region_id, space_read)

    @property
    def bytestring(self):
        byte_string = super(HostDataRead, self).bytestring
        n_requests = self.n_requests
        byte_string += struct.pack("<BB", n_requests, self.sequence_no)
        for i in xrange(n_requests):
            byte_string += struct.pack(
                "<xxBBI", self.channel(i), self.region_id(i),
                self.space_read(i))
        return byte_string


class _HostDataReadHeader(object):
    """
    The HostDataRead contains itself on header with the number of requests
    and a sequence number
    """
    def __init__(self, n_requests, sequence_no):
        self._n_requests = n_requests
        self._sequence_no = sequence_no

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def n_requests(self):
        return self._n_requests


class _HostDataReadAck(object):
    """ Contains a set of acks which refer to each of the channels read
    """
    def __init__(self, channel, region_id, space_read):
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

    def channel(self, ack_id):
        if len(self._channel) > ack_id:
            return self._channel[ack_id]
        else:
            SpinnmanInvalidParameterTypeException(
                "request_id", "integer", "channel ack_id needs to be"
                "comprised between 0 and {0:d}; current value: "
                "{1:d}".format(len(self._channel) - 1, ack_id))

    def region_id(self, ack_id):
        if len(self._region_id) > ack_id:
            return self._region_id[ack_id]
        else:
            SpinnmanInvalidParameterTypeException(
                "request_id", "integer", "region id ack_id needs to be"
                "comprised between 0 and {0:d}; current value: "
                "{1:d}".format(len(self._region_id) - 1, ack_id))

    def space_read(self, ack_id):
        if len(self._space_read) > ack_id:
            return self._space_read[ack_id]
        else:
            SpinnmanInvalidParameterTypeException(
                "request_id", "integer", "start address ack_id needs to be"
                "comprised between 0 and {0:d}; current value: "
                "{1:d}".format(len(self._space_read) - 1, ack_id))
