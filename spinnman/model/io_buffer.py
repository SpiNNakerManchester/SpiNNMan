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


class IOBuffer(object):
    """
    The contents of IOBUF for a core.
    """
    __slots__ = [
        "_iobuf",
        "_x", "_y", "_p"]

    def __init__(self, x: int, y: int, p: int, iobuf: str):
        """
        :param x: The x-coordinate of a chip
        :param y: The y-coordinate of a chip
        :param p: The p-coordinate of a chip
        :param iobuf: The contents of the buffer for the chip
        """
        self._x = x
        self._y = y
        self._p = p
        self._iobuf = iobuf

    @property
    def x(self) -> int:
        """
        The X-coordinate of the chip containing the core.
        """
        return self._x

    @property
    def y(self) -> int:
        """
        The Y-coordinate of the chip containing the core.
        """
        return self._y

    @property
    def p(self) -> int:
        """
        The ID of the core on the chip.
        """
        return self._p

    @property
    def iobuf(self) -> str:
        """
        The contents of the buffer.
        """
        return self._iobuf

    def __str__(self) -> str:
        value = ""
        for line in self._iobuf.split("\n"):
            value += f"{self._x}:{self._y}:{self._p:2n}: {line}\n"
        return value[:-1]
