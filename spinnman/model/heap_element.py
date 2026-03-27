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
from typing import Optional


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

    def __init__(self, block_address: int, next_address: int, free: int):
        """
        :param block_address: The address of this element on the heap
        :param next_address: The address of the next element on the heap
        :param free: The "free" element of the block as read from the heap
        """
        self._block_address = block_address
        self._next_address = next_address
        self._is_free = (free & 0xFFFF0000) != 0xFFFF0000
        self._tag: Optional[int] = None
        self._app_id: Optional[int] = None
        if not self._is_free:
            self._tag = free & 0xFF
            self._app_id = (free >> 8) & 0xFF

    @property
    def block_address(self) -> int:
        """
        The address of the block.
        """
        return self._block_address

    @property
    def next_address(self) -> int:
        """
        The address of the next block, or 0 if none.
        """
        return self._next_address

    @property
    def size(self) -> int:
        """
        The usable size of this block (not including the header).
        """
        return self._next_address - self._block_address - 8

    @property
    def is_free(self) -> bool:
        """
        Whether this block is a free block.
        """
        return self._is_free

    @property
    def tag(self) -> Optional[int]:
        """
        The tag of the block if allocated, or `None` if not.
        """
        return self._tag

    @property
    def app_id(self) -> Optional[int]:
        """
        The application ID of the block if allocated, or `None` if not.
        """
        return self._app_id

    def __str__(self) -> str:
        if self._is_free:
            return f"FREE  0x{self._block_address:8X} SIZE: {self.size:9d}"
        assert self._tag is not None
        assert self._app_id is not None
        return "BLOCK 0x{self._block_address:8X} SIZE: {self.size:9d} " \
               "TAG: {self._tag:3d} APP_ID: {self._app_id:3d}"
