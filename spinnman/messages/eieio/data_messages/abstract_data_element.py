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

from spinn_utilities.abstract_base import AbstractBase, abstractmethod


class AbstractDataElement(object, metaclass=AbstractBase):
    """ A marker interface for possible data elements in the EIEIO data packet
    """

    __slots__ = ()

    @abstractmethod
    def get_bytestring(self, eieio_type):
        """ Get a bytestring for the given type

        :param EIEIOType eieio_type: The type of the message being written
        :return: A bytestring for the element
        :rtype: bytes
        :raise SpinnmanInvalidParameterException:
            If the type is incompatible with the element
        """
