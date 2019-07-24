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


class MulticastMessage(object):
    """ A SpiNNaker Multicast message
    """
    __slots__ = [
        "_key",
        "_payload"]

    def __init__(self, key, payload=None):
        """ A multicast message has a key (determining the target locations) \
            and an optional payload.

        :param key: The key of the packet
        :type key: int
        :param payload: The optional payload of the packet
        :type payload: int
        :raise None: No known exceptions are raised
        """
        self._key = key
        self._payload = payload

    @property
    def key(self):
        """ The key of the packet

        :return: The key
        :rtype: int
        """
        return self._key

    @property
    def payload(self):
        """ The payload of the packet if there is one

        :return: The payload, or None if there is no payload
        :rtype: int
        """
        return self._payload
