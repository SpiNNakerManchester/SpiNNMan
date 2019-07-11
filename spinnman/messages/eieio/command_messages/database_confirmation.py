# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
