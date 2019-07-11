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

from spinnman.messages.eieio.data_messages import (
    EIEIODataMessage, EIEIODataHeader)


def read_eieio_data_message(data, offset):
    """ Reads the content of an EIEIO data message and returns an object\
        identifying the data which was contained in the packet

    :param data: data received from the network as a bytestring
    :type data: str
    :param offset: offset at which the parsing operation should start
    :type offset: int
    :return: an object which inherits from EIEIODataMessage which contains\
        parsed data received from the network
    :rtype:\
        :py:class:`spinnman.messages.eieio.data_messages.EIEIODataMessage`
    """
    eieio_header = EIEIODataHeader.from_bytestring(data, offset)
    offset += eieio_header.size
    return EIEIODataMessage(eieio_header, data, offset)
