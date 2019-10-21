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


class BMPConnectionData(object):
    """ Contains the details of a BMP connection
    """
    __slots__ = [
        "_boards",
        "_cabinet",
        "_frame",
        "_ip_address",
        "_port_num"]

    def __init__(self, cabinet, frame, ip_address, boards, port_num):
        # pylint: disable=too-many-arguments
        self._cabinet = cabinet
        self._frame = frame
        self._ip_address = ip_address
        self._boards = boards
        self._port_num = port_num

    @property
    def cabinet(self):
        """ Get the cabinet number.

        :rtype: int
        """
        return self._cabinet

    @property
    def frame(self):
        """ Get the frame number.

        :rtype: int
        """
        return self._frame

    @property
    def ip_address(self):
        """ Get the IP address of the BMP.

        :rtype: str
        """
        return self._ip_address

    @property
    def boards(self):
        """ The boards to be addressed.

        :rtype: iterable(int)
        """
        return self._boards

    @property
    def port_num(self):
        """ The port number associated with this BMP connection.

        :return: The port number
        """
        return self._port_num

    def __str__(self):
        return "{}:{}:{}:{}:{}".format(
            self._cabinet, self._frame, self._ip_address, self._boards,
            self._port_num)

    def __repr__(self):
        return self.__str__()
