# Copyright (c) 2022 The University of Manchester
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

from typing import Set, Tuple
from spinn_utilities.abstract_base import AbstractBase, abstractproperty


class SpallocMachine(object, metaclass=AbstractBase):
    """
    Represents a spalloc-controlled machine.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ()

    @abstractproperty
    def name(self) -> str:
        """
        The name of the machine.
        """

    @abstractproperty
    def tags(self) -> Set[str]:
        """
        The tags of the machine.
        """

    @abstractproperty
    def width(self) -> int:
        """
        The width of the machine, in boards.
        """

    @abstractproperty
    def height(self) -> int:
        """
        The height of the machine, in boards.
        """

    @abstractproperty
    def dead_boards(self) -> list:
        """
        The dead or out-of-service boards of the machine.
        """

    @abstractproperty
    def dead_links(self) -> list:
        """
        The dead or out-of-service links of the machine.
        """

    @abstractproperty
    def area(self) -> Tuple[int, int]:
        """
        Area of machine, in boards.

        :return: width, height
        :rtype: tuple(int,int)
        """
