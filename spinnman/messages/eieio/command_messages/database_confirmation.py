from spinnman.messages.eieio.command_messages.eieio_command_message\
    import EIEIOCommandMessage
from spinnman.messages.eieio.command_messages.eieio_command_header\
    import EIEIOCommandHeader
from spinnman import constants


class DatabaseConfirmation(EIEIOCommandMessage):

    def __init__(self, database_path=None):
        EIEIOCommandMessage.__init__(
            self, EIEIOCommandHeader(
                constants.EIEIO_COMMAND_IDS.DATABASE_CONFIRMATION.value))
        self._database_path = database_path

    @property
    def database_path(self):
        return self._database_path

    def write_eieio_message(self, writer):
        EIEIOCommandMessage.write_eieio_message(self, writer)
        if self._database_path is not None:
            writer.write_bytes(bytearray(self._database_path))

    @staticmethod
    def read_eieio_command_message(command_header, byte_reader):
        database_path = str(byte_reader.read_bytes())
        if len(database_path) == 0:
            database_path = None
        return DatabaseConfirmation(database_path)
