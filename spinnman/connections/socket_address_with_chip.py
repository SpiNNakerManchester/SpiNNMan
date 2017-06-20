from spinnman.constants import SCP_SCAMP_PORT


class SocketAddressWithChip(object):
    """ The address of a socket and an associated chip
    """

    def __init__(self, hostname, chip_x, chip_y, port_num=SCP_SCAMP_PORT):
        self._hostname = hostname
        self._port_num = port_num
        self._chip_x = chip_x
        self._chip_y = chip_y

    @property
    def hostname(self):
        """ The hostname of the socket

        :return: the hostname
        """
        return self._hostname

    @property
    def port_num(self):
        """ The port number of the socket

        :return: the port
        """
        return self._port_num

    @property
    def chip_x(self):
        """ The x-coordinate of the chip

        :return: the x-coordinate
        """
        return self._chip_x

    @property
    def chip_y(self):
        """ The y-coordinate of the chip

        :return: the y-coordinate
        """
        return self._chip_y

    def __str__(self):
        return "{}:{}:{}:{}".format(
            self._hostname, self._port_num, self._chip_x, self._chip_y)
