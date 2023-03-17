# Copyright (c) 2016 The University of Manchester
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
from spinnman.model.enums import P2PTableRoute

_ONE_WORD = struct.Struct("<I")


class P2PTable(object):
    """
    Represents a P2P routing table read from the machine.
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
        """
        Get the number of bytes to be read for each column of the table.

        :param int height: The height of the machine
        """
        return ((height + 7) // 8) * 4

    @staticmethod
    def get_column_offset(column):
        """
        Get the offset of the next column in the table from the P2P base
        address.

        :param int column: The column to be read
        """
        return (((256 * column) // 8) * 4)

    @property
    def width(self):
        """
        The width of the machine that this table represents.

        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """
        The height of the machine that this table represents.

        :rtype: int
        """
        return self._height

    def iterchips(self):
        """
        Get an iterator of tuples of (x, y) coordinates in the table.

        :rtype: iterable(tuple(int,int))
        """
        return iter(self._routes.keys())

    def is_route(self, x, y):
        """
        Determines if there is a route in the P2P table to the given chip.

        :param int x: The x-coordinate of the chip to look up
        :param int y: The y-coordinate of the chip to look up
        :rtype: bool
        """
        return (
            (x, y) in self._routes and
            self._routes[(x, y)] != P2PTableRoute.NONE)

    def get_route(self, x, y):
        """
        Get the route to follow from this chip to the given chip.

        :param int x: The x-coordinate of the chip to find the route to
        :param int y: The y-coordinate of the chip to find the route to
        :rtype: P2PTableRoute
        """
        if (x, y) in self._routes:
            return self._routes[x, y]
        return P2PTableRoute.NONE
