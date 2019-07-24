# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spinnman.constants import SCP_SCAMP_PORT


class SocketAddressWithChip(object):
    """ The address of a socket and an associated chip
    """
    __slots__ = [
        "_chip_x", "_chip_y",
        "_hostname",
        "_port_num"]

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
