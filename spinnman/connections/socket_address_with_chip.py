"""
SocketAddress
"""
from spinnman import constants

class SocketAddressWithChip(object):
    """
    a data holder for a socket interface for notification protocol.
    """

    def __init__(self, hostname, chip_x, chip_y,
                 port_num=constants.SCP_SCAMP_PORT):
        self._hostname = hostname
        self._port_num = port_num
        self._chip_x = chip_x
        self._chip_y = chip_y

    @property
    def hostname(self):
        """
        getter for the hostname of the socket
        :return: the hostname
        """
        return self._hostname

    @property
    def port_num(self):
        """
        the portnum for the socket
        :return: portnum
        """
        return self._port_num

    @property
    def chip_x(self):
        """
        the chip coord for the scamp connection x axis
        :return: the x axis value for the chip with the scamp connection
        """
        return self._chip_x

    @property
    def chip_y(self):
        """
        the chip coord for the scamp connection y axis
        :return: the y axis value for the chip with the scamp connection
        """
        return self._chip_y

    def __str__(self):
        return "{}:{}:{}:{}".format(self._hostname, self._port_num,
                                    self._chip_x, self._chip_y)

