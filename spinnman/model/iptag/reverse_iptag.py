from spinnman.model.iptag.abstract_iptag import AbstractIPTAG


class ReverseIPTag(AbstractIPTAG):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, port, tag, destination_x, destination_y,
                 destination_p, port_num=1):
        """
        :param port: The UDP port on which SpiNNaker will listen for packets
        :type port: int
        :param tag: The tag of the SDP packet
        :type tag: int
        :param destination_x: The x-coordinate of the chip to send packets to
        :type destination_x: int
        :param destination_y: The y-coordinate of the chip to send packets to
        :type destination_y: int
        :param destination_p: The id of the processor to send packets to
        :type destination_p: int
        :param port_num: The optional port number to use for SDP packets that\
                    formed on the machine (default is 1)
        :type port_num: int
        :raise None: No known exceptions are raised
        """
        AbstractIPTAG.__init__(self, port)
        self._tag = tag
        self._destination_x = destination_x
        self._destination_y = destination_y
        self._destination_p = destination_p
        self._port_num = port_num

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
        return "Reverse IP Tag: tag={} port={} x={} y={} p={}, s_pt={}".format(
            self._tag, self._port, self._destination_x,
            self._destination_y, self._destination_p,
            self._port_num)
