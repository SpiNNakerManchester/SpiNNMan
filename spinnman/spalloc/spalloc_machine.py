# Copyright (c) 2022 The University of Manchester
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

from typing import FrozenSet, Tuple
from spinn_utilities.abstract_base import AbstractBase, abstractmethod


class SpallocMachine(object, metaclass=AbstractBase):
    """
    Represents a Spalloc-controlled machine.

    Don't make this yourself. Use :py:class:`SpallocClient` instead.
    """
    __slots__ = ()

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the machine.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def tags(self) -> FrozenSet[str]:
        """
        The tags of the machine.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def width(self) -> int:
        """
        The width of the machine, in boards.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def height(self) -> int:
        """
        The height of the machine, in boards.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dead_boards(self) -> list:
        """
        The dead or out-of-service boards of the machine.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dead_links(self) -> list:
        """
        The dead or out-of-service links of the machine.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def area(self) -> Tuple[int, int]:
        """
        The width and height of machine
        """
        raise NotImplementedError

# TODO: Add in where-is operations
# Not yet done because not needed immediately for toolchain
