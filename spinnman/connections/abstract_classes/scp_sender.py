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

from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod, abstractproperty)
from .connection import Connection


class SCPSender(Connection, metaclass=AbstractBase):
    """ A sender of SCP messages
    """

    __slots__ = ()

    @abstractmethod
    def get_scp_data(self, scp_request):
        """ Returns the data of an SCP request as it would be sent down this\
            connection
        """

    @abstractmethod
    def send_scp_request(self, scp_request):
        """ Sends an SCP request down this connection

        Messages must have the following properties:

            * source_port is None or 7
            * source_cpu is None or 31
            * source_chip_x is None or 0
            * source_chip_y is None or 0

        tag in the message is optional; if not set, the default set in the\
        constructor will be used.
        sequence in the message is optional; if not set, (sequence number\
        last assigned + 1) % 65536 will be used

        :param AbstractSCPRequest scp_request: message packet to send
        :raise SpinnmanIOException:
            If there is an error sending the message
        """

    @abstractproperty
    def chip_x(self):
        """ The x-coordinate of the chip at which messages sent down this\
            connection will arrive at first

        :rtype: int
        """

    @abstractproperty
    def chip_y(self):
        """ The y-coordinate of the chip at which messages sent down this\
            connection will arrive at first

        :rtype: int
        """
