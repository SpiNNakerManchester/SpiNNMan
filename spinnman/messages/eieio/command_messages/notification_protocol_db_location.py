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

from .eieio_command_message import EIEIOCommandMessage
from .eieio_command_header import EIEIOCommandHeader
from spinnman.constants import EIEIO_COMMAND_IDS


class NotificationProtocolDatabaseLocation(EIEIOCommandMessage):
    """
    Packet which contains the path to the database created by the
    toolchain which is to be used by any software which interfaces with
    SpiNNaker. Also the acknowledgement of that message.

    This message is not sent to SpiNNaker boards but rather to an auxiliary
    tool (e.g., data visualiser).
    """
    __slots__ = [
        "_database_path"]

    def __init__(self, database_path=None):
        """
        :param str database_path:
            The location of the database. If ``None``, this is an
            acknowledgement, stating that the database has now been read.
        """
        super().__init__(EIEIOCommandHeader(EIEIO_COMMAND_IDS.DATABASE))
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
        data = super().bytestring
        if self._database_path is not None:
            data += self._database_path
        return data

    @staticmethod
    def from_bytestring(command_header, data, offset):
        database_path = None
        if len(data) - offset > 0:
            database_path = data[offset:]
        return NotificationProtocolDatabaseLocation(database_path)
