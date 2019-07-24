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


class MachineDimensions(object):
    """ Represents the size of a machine in chips
    """
    __slots__ = [
        "_height",
        "_width"]

    def __init__(self, width, height):
        """
        :param width: The width of the machine in chips
        :type width: int
        :param height: The height of the machine in chips
        :type height: int
        :raise None: No known exceptions are raised
        """
        self._width = width
        self._height = height

    @property
    def width(self):
        """ The width of the machine in chips

        :return: The width
        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """ The height of the machine in chips

        :return: The height
        :rtype: int
        """
        return self._height
