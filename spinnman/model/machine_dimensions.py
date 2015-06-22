class MachineDimensions(object):
    """ Represents the size of a machine in chips
    """

    def __init__(self, width, height):
        """
        :param width: The width of the machine in chips
        :type width: int
        :param height: The height of the machine in chips
        :type height: int
        :raise None: No known exceptions are raised
        """
        self._width = width
        self._height = height

    @property
    def width(self):
        """ The width of the machine in chips

        :return: The width
        :rtype: int
        """
        return self._width

    @property
    def height(self):
        """ The height of the machine in chips

        :return: The height
        :rtype: int
        """
        return self._height
