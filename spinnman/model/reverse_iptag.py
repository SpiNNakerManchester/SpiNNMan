class ReverseIPTag(object):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, address, port, tag, destination_x, destination_y,
                 destination_p, port_num=1):
        """
        :param address: The IP address to which SCP packets with the reverse\
         tag will be sent
        :type address: str
        :param port: The port to which the SCP packets with the reverse tag \
        will be sent
        :type port: int
        :param tag: The tag of the SCP packet
        :type tag: int
        :raise None: No known exceptions are raised
        """
        self._address = address
        self._port = port
        self._tag = tag
        self._destination_x = destination_x
        self._destination_y = destination_y
        self._destination_p = destination_p
        self._port_num = port_num

    @property
    def address(self):
        """ Return the IP address of the tag
        """
        return self._address

    @property
    def port(self):
        """ Return the port of the tag
        """
        return self._port

    @property
    def port_num(self):
        """returns the port num of the tag
        :return:
        """
        return self._port_num

    @property
    def tag(self):
        """ Return the tag of the packet
        """
        return self._tag

    @property
    def destination_x(self):
        """:return: the destination x for a reverse ip tag
        """
        return self._destination_x

    @property
    def destination_y(self):
        """:return: the destination y for a reverse ip tag
        """
        return self._destination_y

    @property
    def destination_p(self):
        """:return: the destination p for a reverse ip tag
        """
        return self._destination_p

    def set_tag(self, new_tag):
        """ sets the tag of the packet
        """
        self._tag = new_tag

    def __str__(self):
        return "{} {:5} {} {} {} {}".format(
            self._tag, self._port, self._address, self._destination_x,
            self._destination_y, self._destination_p)
