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


class MachineDimensions(object):
    """
    Represents the size of a machine in chips.
    """
    __slots__ = [
        "_height",
        "_width"]

    def __init__(self, width, height):
        """
        :param int width: The width of the machine in chips
        :param int height: The height of the machine in chips
        """
        self._width = width
        self._height = height

    @property
    def width(self):
        """
        The width of the machine in chips.

        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """
        The height of the machine in chips.

        :rtype: int
        """
        return self._height
