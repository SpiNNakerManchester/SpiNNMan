from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman import constants
from spinnman.messages.eieio.create_eieio_data import read_eieio_data_message


class HostSendSequencedData(EIEIOCommandMessage):

    def __init__(self, region_id, sequence_no, eieio_data_message):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.HOST_SEND_SEQUENCED_DATA.value))
        self._region_id = region_id
        self._sequence_no = sequence_no
        self._eieio_data_message = eieio_data_message

    @property
    def region_id(self):
        return self._region_id

    @property
    def sequence_no(self):
        return self._sequence_no

    @property
    def eieio_data_message(self):
        return self._eieio_data_message

    @staticmethod
    def get_min_packet_length():
        return 4

    @staticmethod
    def read_eieio_command_message(command_header, byte_reader):
        region_id = byte_reader.read_byte()
        sequence_no = byte_reader.read_byte()
        eieio_data_message = read_eieio_data_message(byte_reader)
        return HostSendSequencedData(region_id, sequence_no,
                                     eieio_data_message)

    def write_eieio_message(self, writer):
        EIEIOCommandMessage.write_eieio_message(self, writer)
        writer.write_byte(self._region_id)
        writer.write_byte(self._sequence_no)
        self._eieio_data_message.write_eieio_message(writer)
