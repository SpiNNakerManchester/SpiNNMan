class BMPConnectionData(object):
    """ Contains the details of a BMP connection
    """

    def __init__(self, cabinet, frame, ip_address, boards, port_num):
        self._cabinet = cabinet
        self._frame = frame
        self._ip_address = ip_address
        self._boards = boards
        self._port_num = port_num

    @property
    def cabinet(self):
        """ Get the cabinet number

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """ Get the frame number

        :rtype: int
        """
        return self._frame

    @property
    def ip_address(self):
        """ Get the IP address of the BMP

        :rtype: str
        """
        return self._ip_address

    @property
    def boards(self):
        """ Iterable of integers for the boards to be addressed

        :rtype: iterable of int
        """
        return self._boards

    @property
    def port_num(self):
        """ The port number associated with this BMP connection

        :return: The port number
        """
        return self._port_num

    def __str__(self):
        return "{}:{}:{}:{}:{}".format(
            self._cabinet, self._frame, self._ip_address, self._boards,
            self._port_num)

    def __repr__(self):
        return self.__str__()
