from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman import constants
import struct


class HostDataRead(EIEIOCommandMessage):

    def __init__(self, region_id, sequence_no, space_read):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.NEW_BUFFERS.value))
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._space_read = space_read

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def region_id(self):
        return self._region_id

    @property
    def space_read(self):
        return self._space_read

    @staticmethod
    def get_min_packet_length():
        return 8

    @staticmethod
    def from_bytestring(command_header, data, offset):
        region_id, sequence_no, space = struct.unpack_from(
            "<BBI", data, offset)
        return HostDataRead(region_id, sequence_no, space)

    @property
    def bytestring(self):
        return super(HostDataRead, self).bytestring + struct.pack(
            "<BBI", self._region_id, self._sequence_no, self._space_read)
