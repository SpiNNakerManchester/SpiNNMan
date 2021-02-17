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
from spinnman.model.enums import P2PTableRoute

_ONE_WORD = struct.Struct("<I")


class P2PTable(object):
    """ Represents a P2P routing table read from the machine.
    """
    __slots__ = [
        "_height",
        "_routes",
        "_width"]

    def __init__(self, width, height, column_data):
        """
        :param int width:
        :param int height:
        :param bytes column_data:
        """
        self._routes = dict()
        self._width = width
        self._height = height
        for x in range(len(column_data)):
            y = 0
            pos = 0
            while y < height:
                data, offset = column_data[x]
                next_word, = _ONE_WORD.unpack_from(data, offset + (pos * 4))
                pos += 1
                for entry in range(min(8, height - y)):
                    route = P2PTableRoute((next_word >> (3 * entry)) & 0b111)
                    if route is not P2PTableRoute.NONE:
                        self._routes[x, y] = route
                    y += 1

    @staticmethod
    def get_n_column_bytes(height):
        """ Get the number of bytes to be read for each column of the table.

        :param int height: The height of the machine
        """
        return ((height + 7) // 8) * 4

    @staticmethod
    def get_column_offset(column):
        """ Get the offset of the next column in the table from the P2P base\
            address.

        :param int column: The column to be read
        """
        return (((256 * column) // 8) * 4)

    @property
    def width(self):
        """ The width of the machine that this table represents.

        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """ The height of the machine that this table represents.

        :rtype: int
        """
        return self._height

    def iterchips(self):
        """ Get an iterator of tuples of (x, y) coordinates in the table

        :rtype: iterable(tuple(int,int))
        """
        return iter(self._routes.keys())

    def is_route(self, x, y):
        """ Determines if there is a route in the P2P table to the given chip.

        :param int x: The x-coordinate of the chip to look up
        :param int y: The y-coordinate of the chip to look up
        :rtype: bool
        """
        return (
            (x, y) in self._routes and
            self._routes[(x, y)] != P2PTableRoute.NONE)

    def get_route(self, x, y):
        """ Get the route to follow from this chip to the given chip.

        :param int x: The x-coordinate of the chip to find the route to
        :param int y: The y-coordinate of the chip to find the route to
        :rtype: P2PTableRoute
        """
        if (x, y) in self._routes:
            return self._routes[x, y]
        return P2PTableRoute.NONE
