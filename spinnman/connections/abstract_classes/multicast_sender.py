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

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


class MulticastSender(Connection, metaclass=AbstractBase):
    """ A sender of Multicast messages
    """

    __slots__ = ()

    @abstractmethod
    def get_input_chips(self):
        """ Get a list of chips which identify the chips to which this sender\
            can send multicast packets directly

        :return: The coordinates, (x, y), of the chips
        :rtype: iterable(tuple(int, int))
        """

    @abstractmethod
    def send_multicast_message(self, multicast_message):
        """ Sends a SpiNNaker multicast message using this connection

        :param MulticastMessage multicast_message: The message to be sent
        :raise SpinnmanIOException:
            If there is an error sending the message
        """
