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


class HeapElement(object):
    """
    An element of one of the heaps on SpiNNaker.
    """

    __slots__ = [
        # A pointer to the block
        "_block_address",
        # A pointer to the next block
        "_next_address",
        # True if the block is free
        "_is_free",
        # The tag of the block
        "_tag",
        # The app ID of the block
        "_app_id"
    ]

    def __init__(self, block_address, next_address, free):
        """
        :param int block_address: The address of this element on the heap
        :param int next_address: The address of the next element on the heap
        :param int free: The "free" element of the block as read from the heap
        """
        self._block_address = block_address
        self._next_address = next_address
        self._is_free = (free & 0xFFFF0000) != 0xFFFF0000
        self._tag = None
        self._app_id = None
        if not self._is_free:
            self._tag = free & 0xFF
            self._app_id = (free >> 8) & 0xFF

    @property
    def block_address(self):
        """
        The address of the block.

        :rtype: int
        """
        return self._block_address

    @property
    def next_address(self):
        """
        The address of the next block, or 0 if none.

        :rtype: int
        """
        return self._next_address

    @property
    def size(self):
        """
        The usable size of this block (not including the header).

        :rtype: int
        """
        return self._next_address - self._block_address - 8

    @property
    def is_free(self):
        """
        Whether this block is a free block.

        :rtype: bool
        """
        return self._is_free

    @property
    def tag(self):
        """
        The tag of the block if allocated, or `None` if not.

        :rtype: int or None
        """
        return self._tag

    @property
    def app_id(self):
        """
        The application ID of the block if allocated, or `None` if not.

        :rtype: int or None
        """
        return self._app_id

    def __str__(self):
        if self._is_free:
            return "FREE  0x{:8X} SIZE: {:9d}".format(
                self._block_address, self.size)
        return "BLOCK 0x{:8X} SIZE: {:9d} TAG: {:3d} APP_ID: {:3d}".format(
            self._block_address, self.size, self._tag, self._app_id)
