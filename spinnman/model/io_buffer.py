class IOBuffer(object):
    """ The contents of IOBUF for a core
    """

    def __init__(self, x, y, p, iobuf):
        """
        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :param p: The p-coordinate of a chip
        :type p: int
        :param iobuf: The contents of the buffer for the chip
        :type iobuf: str
        :raise None: No known exceptions are raised
        """
        self._x = x
        self._y = y
        self._p = p
        self._iobuf = iobuf

    @property
    def x(self):
        """ The x-coordinate of the chip containing the core

        :return: The x-coordinate of the chip
        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip containing the core

        :return: The y-coordinate of the chip
        :rtype: int
        """
        return self._y

    @property
    def p(self):
        """ The id of the core on the chip

        :return: The id of the core
        :rtype: int
        """
        return self._p

    @property
    def iobuf(self):
        """ The contents of the buffer

        :return: The contents of the buffer
        :rtype: str
        """
        return self._iobuf

    def __str__(self):
        value = ""
        for line in self._iobuf.split("\n"):
            value += "{}:{}:{:2n}: {}\n".format(
                self._x, self._y, self._p, line)
        return value[:-1]
