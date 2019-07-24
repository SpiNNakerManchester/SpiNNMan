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
from spinnman.messages.scp.enums import SCPResult

_TWO_SHORTS = struct.Struct("<2H")


class SCPResponseHeader(object):
    """ Represents the header of an SCP Response
    """
    __slots__ = [
        "_result",
        "_sequence"]

    def __init__(self, result=None, sequence=None):
        """
        """
        self._result = result
        self._sequence = sequence

    @property
    def result(self):
        """ The result of the SCP response

        :return: The result
        :rtype: :py:class:`spinnman.messages.scp.scp_result.SCPResult`
        """
        return self._result

    @property
    def sequence(self):
        """ The sequence number of the SCP response

        :return: The sequence number of the packet, between 0 and 65535
        :rtype: int
        """
        return self._sequence

    @staticmethod
    def from_bytestring(data, offset):
        """ Read a header from a bytestring

        :param data: The bytestring to read from
        :type data: str
        :param offset:
        """
        result, sequence = _TWO_SHORTS.unpack_from(data, offset)
        return SCPResponseHeader(SCPResult(result), sequence)
