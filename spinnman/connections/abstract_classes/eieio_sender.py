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

from six import add_metaclass
from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from .connection import Connection


@add_metaclass(AbstractBase)
class EIEIOSender(Connection):
    """ A sender of EIEIO messages
    """

    __slots__ = ()

    @abstractmethod
    def send_eieio_message(self, eieio_message):
        """ Sends an EIEIO message down this connection

        :param eieio_message: The EIEIO message to be sent
        :type eieio_message: \
            :py:class:`spinnman.messages.eieio.AbstractEIEIOMessage`
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error sending the message
        """
