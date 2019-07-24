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
class SpinnakerBootSender(Connection):
    """ A sender of SpiNNaker Boot messages
    """

    __slots__ = ()

    @abstractmethod
    def send_boot_message(self, boot_message):
        """ Sends a SpiNNaker boot message using this connection.

        :param boot_message: The message to be sent
        :type boot_message:\
            :py:class:`spinnman.messages.spinnaker_boot.SpinnakerBootMessage`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error sending the message
        """
