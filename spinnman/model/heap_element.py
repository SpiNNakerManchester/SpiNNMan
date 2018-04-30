class HeapElement(object):
    """ An element of one of the heaps on SpiNNaker
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
        # The app id of the block
        "_app_id"
    ]

    def __init__(self, block_address, next_address, free):
        """
        :param block_address: The address of this element on the heap
        :param next_address: The address of the next element on the heap
        :param free: The "free" element of the block as read from the heap
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
        """ The address of the block
        """
        return self._block_address

    @property
    def next_address(self):
        """ The address of the next block, or 0 if none
        """
        return self._next_address

    @property
    def size(self):
        """ The usable size of this block (not including the header)
        """
        return self._next_address - self._block_address - 8

    @property
    def is_free(self):
        """ True if this block is a free block, False otherwise
        """
        return self._is_free

    @property
    def tag(self):
        """ The tag of the block if allocated, or None if not
        """
        return self._tag

    @property
    def app_id(self):
        """ The app ID of the block if allocated, or None if not
        """
        return self._app_id

    def __str__(self):
        if self._is_free:
            return "FREE  0x{:8X} SIZE: {:9d}".format(
                self._block_address, self.size)
        return "BLOCK 0x{:8X} SIZE: {:9d} TAG: {:3d} APP_ID: {:3d}".format(
            self._block_address, self.size, self._tag, self._app_id)
