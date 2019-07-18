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

from spinnman.messages.eieio import AbstractEIEIOMessage


class EIEIOCommandMessage(AbstractEIEIOMessage):
    """ An EIEIO command message
    """
    __slots__ = [
        "_data",
        "_eieio_command_header",
        "_offset"]

    def __init__(self, eieio_command_header, data=None, offset=0):
        """
        :param eieio_command_header: The header of the message
        :type eieio_command_header:\
            :py:class:`spinnman.messages.eieio.command_messages.EIEIOCommandHeader`
        :param data: Optional incoming data
        :type data: str
        :param offset: Offset into the data where valid data begins
        :type offset: int
        """
        # The header
        self._eieio_command_header = eieio_command_header

        # The data
        self._data = data
        self._offset = offset

    @property
    def eieio_header(self):
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
    def bytestring(self):
        return self._eieio_command_header.bytestring

    @staticmethod
    def get_min_packet_length():
        return 2

    def __str__(self):
        return "EIEIOCommandMessage:{}".format(self._eieio_command_header)

    def __repr__(self):
        return self.__str__()
