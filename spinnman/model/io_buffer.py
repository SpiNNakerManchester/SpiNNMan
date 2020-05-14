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


class IOBuffer(object):
    """ The contents of IOBUF for a core
    """
    __slots__ = [
        "_iobuf",
        "_x", "_y", "_p"]

    def __init__(self, x, y, p, iobuf):
        """
        :param int x: The x-coordinate of a chip
        :param int y: The y-coordinate of a chip
        :param int p: The p-coordinate of a chip
        :param str iobuf: The contents of the buffer for the chip
        """
        self._x = x
        self._y = y
        self._p = p
        self._iobuf = iobuf

    @property
    def x(self):
        """ The x-coordinate of the chip containing the core

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip containing the core

        :rtype: int
        """
        return self._y

    @property
    def p(self):
        """ The ID of the core on the chip

        :rtype: int
        """
        return self._p

    @property
    def iobuf(self):
        """ The contents of the buffer

        :rtype: str
        """
        return self._iobuf

    def __str__(self):
        value = ""
        for line in self._iobuf.split("\n"):
            value += "{}:{}:{:2n}: {}\n".format(
                self._x, self._y, self._p, line)
        return value[:-1]
