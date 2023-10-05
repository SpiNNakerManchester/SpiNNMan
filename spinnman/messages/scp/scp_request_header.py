# Copyright (c) 2014 The University of Manchester
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

import struct

_TWO_SHORTS = struct.Struct("<2H")


class SCPRequestHeader(object):
    """
    Represents the header of an SCP Request
    Each optional parameter in the constructor can be set to a value other
    than `None` once, after which it is immutable.  It is an error to set a
    parameter that is not currently `None`.
    """
    __slots__ = [
        "_command",
        "_sequence"]

    def __init__(self, command, sequence=0):
        """
        :param SCPCommand command: The SCP command
        :param int sequence:
            The number of the SCP packet in order of all packets
            sent or received, between 0 and 65535
        :raise SpinnmanInvalidParameterException:
            If one of the parameters is incorrect
        """
        self._command = command
        self._sequence = sequence

    @property
    def command(self):
        """
        The command of the SCP packet.

        :rtype: SCPCommand
        """
        return self._command

    @property
    def sequence(self):
        """
        The sequence number of the SCP packet, between 0 and 65535.

        :rtype: int
        """
        return self._sequence

    @sequence.setter
    def sequence(self, sequence):
        """
        Set the sequence number of the SCP packet.

        :param int sequence: The sequence number to set, between 0 and 65535
        :raise SpinnmanInvalidParameterException:
            If the sequence is out of range, or if it has already been set
        """
        self._sequence = sequence

    @property
    def bytestring(self):
        """
        The header as a byte-string.

        :rtype: bytes
        """
        return _TWO_SHORTS.pack(self._command.value, self._sequence)
