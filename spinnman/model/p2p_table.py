import struct

from spinnman.model.enums import P2PTableRoute


class P2PTable(object):
    """ Represents a P2P table read from the machine
    """

    def __init__(self, width, height, column_data):
        self._routes = dict()
        self._width = width
        self._height = height
        for x in range(len(column_data)):
            y = 0
            pos = 0
            while y < height:
                (data, offset) = column_data[x]
                next_word = struct.unpack_from(
                    "<I", data, offset + (pos * 4))[0]
                pos += 1
                for entry in range(min(8, height - y)):
                    route = P2PTableRoute((next_word >> (3 * entry)) & 0b111)
                    if route is not P2PTableRoute.NONE:
                        self._routes[x, y] = route
                    y += 1

    @staticmethod
    def get_n_column_bytes(height):
        """ Get the number of bytes to be read for each column of the table

        :param height: The height of the machine
        """
        return ((height + 7) // 8) * 4

    @staticmethod
    def get_column_offset(column):
        """ Get the offset of the next column in the table from the P2P base\
            address

        :param column: The column to be read
        """
        return (((256 * column) // 8) * 4)

    @property
    def width(self):
        """ The width of the machine that this table represents
        """
        return self._width

    @property
    def height(self):
        """ The height of the machine that this table represents
        """
        return self._height

    def iterchips(self):
        """ Get an iterator of tuples of (x, y) coordinates in the table
        """
        return self._routes.iterkeys()

    def is_route(self, x, y):
        """ Determines if there is a route in the P2P table to the given chip

        :param x: The x-coordinate of the chip to look up
        :param y: The y-coordinate of the chip to look up
        """
        return (
            (x, y) in self._routes and
            self._routes[(x, y)] != P2PTableRoute.NONE)

    def get_route(self, x, y):
        """ Get the route to follow from this chip to the given chip

        :param x: The x-coordinate of the chip to find the route to
        :param y: The y-coordinate of the chip to find the route to
        """
        if (x, y) in self._routes:
            return self._routes[x, y]
        return P2PTableRoute.NONE
