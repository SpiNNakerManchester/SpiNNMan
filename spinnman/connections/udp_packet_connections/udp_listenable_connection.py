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

from spinn_utilities.overrides import overrides
from spinnman.connections.abstract_classes import Listenable
from .udp_connection import UDPConnection


class UDPListenableConnection(UDPConnection, Listenable):

    def __init__(self, local_host=None, local_port=None, remote_host=None,
                 remote_port=None):
        super(UDPListenableConnection, self).__init__(
            local_host=local_host, local_port=local_port,
            remote_host=remote_host, remote_port=remote_port)

    @overrides(Listenable.get_receive_method)
    def get_receive_method(self):
        return self.receive
