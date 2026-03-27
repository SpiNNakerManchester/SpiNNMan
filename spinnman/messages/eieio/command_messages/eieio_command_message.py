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

from typing import Optional
from spinn_utilities.overrides import overrides
from spinnman.messages.eieio import AbstractEIEIOMessage
from spinnman.messages.eieio.command_messages import EIEIOCommandHeader


class EIEIOCommandMessage(AbstractEIEIOMessage):
    """
    An EIEIO command message.
    """
    __slots__ = (
        "_data",
        "_eieio_command_header",
        "_offset")

    def __init__(self, eieio_command_header: EIEIOCommandHeader,
                 data: Optional[bytes] = None, offset: int = 0):
        """
        :param eieio_command_header:
            The header of the message
        :param data: Optional incoming data
        :param offset: Offset into the data where valid data begins
        """
        # The header
        self._eieio_command_header = eieio_command_header

        # The data
        self._data = data
        self._offset = offset

    @property
    @overrides(AbstractEIEIOMessage.eieio_header)
    def eieio_header(self) -> EIEIOCommandHeader:
        """ Gets the eieio_header passed into the init. """
        return self._eieio_command_header

    @property
    def data(self) -> Optional[bytes]:
        """ Gets the data passed into the init (if applicable). """
        return self._data

    @property
    def offset(self) -> int:
        """ Gets the offset passed into the init """
        return self._offset

    @staticmethod
    def from_bytestring(command_header: EIEIOCommandHeader, data: bytes,
                        offset: int) -> "EIEIOCommandMessage":
        """
        Creates an EIEIOCommandMessage based on the supplied information.

        :param command_header:
        :param data:
        :param offset:
        :returns: The created EIEIOCommandMessage
        """
        return EIEIOCommandMessage(command_header, data, offset)

    @property
    def bytestring(self) -> bytes:
        """
        The eieio_command_header passed into the init as a byte string.
        """
        return self._eieio_command_header.bytestring

    @staticmethod
    def get_min_packet_length() -> int:
        """
        :returns: the min packet length for this type.
        """
        return 2

    def __str__(self) -> str:
        return f"EIEIOCommandMessage:{self._eieio_command_header}"

    def __repr__(self) -> str:
        return self.__str__()
