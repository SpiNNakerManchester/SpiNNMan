from spinnman import constants
from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader


class PaddingRequest(EIEIOCommandMessage):

    def __init__(self, size_to_pad):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.EVENT_PADDING.value))
        self._size_to_pad = size_to_pad

    @property
    def size_to_pad(self):
        return self._size_to_pad

    @staticmethod
    def get_min_packet_length():
        return 2

    @staticmethod
    def read_eieio_command_message(command_header, byte_reader):
        padding = byte_reader.read_byte()
        return PaddingRequest(len(padding))

    def write_eieio_message(self, writer):
        EIEIOCommandMessage.write_eieio_message(self, writer)
        writer.write_bytes([0 for _ in range(self._size_to_pad)])
