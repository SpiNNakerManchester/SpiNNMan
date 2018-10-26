from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class DatabaseConfirmation(EIEIOCommandMessage):
    """ Packet which contains the path to the database created by the\
        toolchain which is to be used by any software which interfaces with\
        SpiNNaker.
    """
    __slots__ = [
        "_database_path"]

    def __init__(self, database_path=None):
        super(DatabaseConfirmation, self).__init__(EIEIOCommandHeader(
            EIEIO_COMMAND_IDS.DATABASE_CONFIRMATION))
        self._database_path = None
        if database_path is not None:
            self._database_path = database_path.encode()

    @property
    def database_path(self):
        if self._database_path is not None:
            return self._database_path.decode()
        else:
            return None

    @property
    def bytestring(self):
        data = super(DatabaseConfirmation, self).bytestring
        if self._database_path is not None:
            data += self._database_path
        return data

    @staticmethod
    def from_bytestring(command_header, data, offset):
        database_path = None
        if len(data) - offset > 0:
            database_path = data[offset:]
        return DatabaseConfirmation(database_path)
