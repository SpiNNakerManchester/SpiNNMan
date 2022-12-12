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
from .abstract_multi_connection_process_connection_selector import (
    AbstractMultiConnectionProcessConnectionSelector)


class FixedConnectionSelector(
        AbstractMultiConnectionProcessConnectionSelector):
    """ A connection selector that only uses a single connection.
    """
    __slots__ = ("__connection", )

    def __init__(self, connection):
        """
        :param SCAMPConnection connection:
            The connection to be used
        """
        self.__connection = connection

    @overrides(
        AbstractMultiConnectionProcessConnectionSelector.get_next_connection)
    def get_next_connection(self, message):
        return self.__connection
