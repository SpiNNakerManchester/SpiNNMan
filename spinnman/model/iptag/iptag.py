from spinnman.model.iptag.abstract_iptag import AbstractIPTAG


class IPTag(AbstractIPTAG):
    """ Used to hold data that is contained within an IPTag
    """

    def __init__(self, address, port, tag, strip_sdp=False):
        """
        :param address: The IP address to which SCP packets with the tag will\
                    be sent
        :type address: str
        :param port: The port to which the SCP packets with the tag will be\
                    sent
        :type port: int
        :param tag: The tag of the SCP packet
        :type tag: int
        :param strip_sdp: Indicates whether the SDP header should be removed
        :type strip_sdp: bool
        :raise None: No known exceptions are raised
        """
        AbstractIPTAG.__init__(self, port)
        self._address = address
        self._tag = tag
        self._strip_sdp = strip_sdp

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

    @property
    def strip_sdp(self):
        """ Return if the sdp header is to be stripped
        """
        return self._strip_sdp

    def string_representation(self):
        return self.__str__()

    def __str__(self):
        return "IP Tag: tag={} port={} address={}".format(
                self._tag, self._port, self._address)
