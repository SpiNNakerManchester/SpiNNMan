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

import struct

_DS = struct.Struct("<4I4B")


class BigDataInfo(object):
    """ Represents the big data information read via an SCP command
    """
    __slots__ = [
        "_ip_address", "_port", "_n_sent", "_n_received",
        "_n_discard_not_idle", "_x", "_y"
    ]

    def __init__(self, big_data_data, offset, x, y):
        """
        :param big_data_data: The data from the SCP response
        :type big_data_data: bytearray
        :param offset: The offset into the data where the data starts
        :type offset: int
        :param x: The x-coordinate of the chip that this data is from
        :param y: The y-coordinate of the chip that this data is from
        """
        (self._port, self._n_sent, self._n_received, self._n_discard_not_idle,
         ip_1, ip_2, ip_3, ip_4) = _DS.unpack_from(big_data_data, offset)

        self._ip_address = "{}.{}.{}.{}".format(ip_1, ip_2, ip_3, ip_4)

        self._x = x
        self._y = y

    @property
    def x(self):
        """ The x-coordinate of the chip that this data is from

        :rtype: int
        """
        return self._x

    @property
    def y(self):
        """ The y-coordinate of the chip that this data is from

        :rtype: int
        """
        return self._y

    @property
    def ip_address(self):
        """ The IP address of the receiver of the data
        """
        return self._ip_address

    @property
    def port(self):
        """ The port of the receiver of the data
        """
        return self._port

    @property
    def n_sent(self):
        """ The number of packets successfully sent by the Big Data core
        """
        return self._n_sent

    @property
    def n_received(self):
        """ The number of packets successfully received by the Big Data core
        """
        return self._n_received

    @property
    def n_discard_not_idle(self):
        """ The number of incoming packets discarded because the receiver is\
            not idle
        """
        return self._n_discard_not_idle

    def __repr__(self):
        return ("x:{} y:{} ip_address:{} port:{} n_sent:{} n_received:{}"
                " n_discard_not_idle:{}".format(
                    self.x, self.y, self.ip_address, self.port, self.n_sent,
                    self.n_received, self.n_discard_not_idle))
