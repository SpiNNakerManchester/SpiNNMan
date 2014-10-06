class ReverseIPTag(object):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, address, port, tag):
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
    def tag(self):
        """ Return the tag of the packet
        """
        return self._tag

    def set_tag(self, new_tag):
        """ sets the tag of the packet
        """
        self._tag = new_tag

    def __str__(self):
        return "{} {:5} {}".format(self._tag, self._port, self._address)
