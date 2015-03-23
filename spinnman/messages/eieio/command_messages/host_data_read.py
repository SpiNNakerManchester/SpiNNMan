from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman import constants


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
    def read_eieio_command_message(command_header, byte_reader):
        region_id = byte_reader.read_byte()
        sequence_no = byte_reader.read_byte()
        space = byte_reader.read_int()
        return HostDataRead(region_id, sequence_no, space)

    def write_eieio_message(self, writer):
        EIEIOCommandMessage.write_eieio_message(self, writer)
        writer.write_byte(self._region_id)
        writer.write_byte(self._sequence_no)
        writer.write_int(self._space_read)
