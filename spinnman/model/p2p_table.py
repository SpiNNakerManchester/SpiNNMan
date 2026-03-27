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
from typing import Dict, Iterable, List, Tuple
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

    def __init__(self, width: int, height: int,
                 column_data: List[Tuple[bytes, int]]):
        """
        :param width:
        :param height:
        :param column_data:
        """
        self._routes: Dict[Tuple[int, int], P2PTableRoute] = dict()
        self._width = width
        self._height = height
        for x, (data, offset) in enumerate(column_data):
            y = 0
            pos = 0
            while y < height:
                next_word, = _ONE_WORD.unpack_from(data, offset + (pos * 4))
                pos += 1
                for entry in range(min(8, height - y)):
                    route = P2PTableRoute((next_word >> (3 * entry)) & 0b111)
                    if route is not P2PTableRoute.NONE:
                        self._routes[x, y] = route
                    y += 1

    @staticmethod
    def get_n_column_bytes(height: int) -> int:
        """
        :param height: The height of the machine
        :returns: The number of bytes to be read for each column of the table.
        """
        return ((height + 7) // 8) * 4

    @staticmethod
    def get_column_offset(column: int) -> int:
        """
        :param column: The column to be read
        :returns: the offset of the next column in the table
           from the P2P base address.
        """
        return (((256 * column) // 8) * 4)

    @property
    def width(self) -> int:
        """
        The width of the machine that this table represents.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height of the machine that this table represents.
        """
        return self._height

    def iterchips(self) -> Iterable[Tuple[int, int]]:
        """
        :returns: An iterator of tuples of (x, y) coordinates in the table.
        """
        return iter(self._routes.keys())

    def is_route(self, x: int, y: int) -> bool:
        """
        :param x: The x-coordinate of the chip to look up
        :param y: The y-coordinate of the chip to look up
        :returns: True if there is a route in the P2P table to the given chip.
        """
        return (
            (x, y) in self._routes and
            self._routes[(x, y)] != P2PTableRoute.NONE)

    def get_route(self, x: int, y: int) -> P2PTableRoute:
        """
        :param x: The x-coordinate of the chip to find the route to
        :param y: The y-coordinate of the chip to find the route to
        :returns: The route to follow from this chip to the given chip.
        """
        return self._routes.get((x, y), P2PTableRoute.NONE)

    @property
    def n_routes(self) -> int:
        """ The number of routes in the table
        """
        return len(self._routes)
