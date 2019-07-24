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

import struct

_TWO_SHORTS = struct.Struct("<2H")


class SCPRequestHeader(object):
    """ Represents the header of an SCP Request
        Each optional parameter in the constructor can be set to a value other\
        than None once, after which it is immutable.  It is an error to set a\
        parameter that is not currently None.
    """
    __slots__ = [
        "_command",
        "_sequence"]

    def __init__(self, command, sequence=0):
        """

        :param command: The SCP command
        :type command: :py:class:`spinnman.messages.scp.scp_command.SCPCommand`
        :param sequence: The number of the SCP packet in order of all packets\
            sent or received, between 0 and 65535
        :type sequence: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: \
            If one of the parameters is incorrect
        """
        self._command = command
        self._sequence = sequence

    @property
    def command(self):
        """ The command of the SCP packet

        :return: The command
        :rtype: :py:class:`spinnman.messages.scp.scp_command.SCPCommand`
        """
        return self._command

    @property
    def sequence(self):
        """ The sequence number of the SCP packet

        :return: The sequence number of the packet, between 0 and 65535
        :rtype: int
        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        """ Set the sequence number of the SCP packet

        :param sequence: The sequence number to set, between 0 and 65535
        :type sequence: int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: \
            If the sequence is out of range, or if it has already been set
        """
        self._sequence = sequence

    @property
    def bytestring(self):
        """ The header as a bytestring

        :return: The header as a bytestring
        :rtype: str
        """
        return _TWO_SHORTS.pack(self._command.value, self._sequence)
