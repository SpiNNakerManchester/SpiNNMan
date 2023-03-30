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
from spinn_utilities.overrides import overrides
from spinnman.messages.eieio import AbstractEIEIOMessage


class EIEIOCommandMessage(AbstractEIEIOMessage):
    """
    An EIEIO command message.
    """
    __slots__ = [
        "_data",
        "_eieio_command_header",
        "_offset"]

    def __init__(self, eieio_command_header, data=None, offset=0):
        """
        :param EIEIOCommandHeader eieio_command_header:
            The header of the message
        :param bytes data: Optional incoming data
        :param int offset: Offset into the data where valid data begins
        """
        # The header
        self._eieio_command_header = eieio_command_header

        # The data
        self._data = data
        self._offset = offset

    @property
    @overrides(AbstractEIEIOMessage.eieio_header)
    def eieio_header(self):
        """
        :rtype: EIEIOCommandHeader
        """
        return self._eieio_command_header

    @property
    def data(self):
        return self._data

    @property
    def offset(self):
        return self._offset

    @staticmethod
    def from_bytestring(command_header, data, offset):
        return EIEIOCommandMessage(command_header, data, offset)

    @property
    @overrides(AbstractEIEIOMessage.bytestring)
    def bytestring(self):
        return self._eieio_command_header.bytestring

    @staticmethod
    def get_min_packet_length():
        return 2

    def __str__(self):
        return f"EIEIOCommandMessage:{self._eieio_command_header}"

    def __repr__(self):
        return self.__str__()
