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
class SDPSender(Connection):
    """ A sender of SDP messages.
    """

    __slots__ = ()

    @abstractmethod
    def send_sdp_message(self, sdp_message):
        """ Sends an SDP message down this connection

        :param sdp_message: The SDP message to be sent
        :type sdp_message: spinnman.messages.sdp.sdp_message.SDPMessage
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: \
            If there is an error sending the message.
        """
