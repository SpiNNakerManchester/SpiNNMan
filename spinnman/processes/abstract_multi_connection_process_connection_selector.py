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


@add_metaclass(AbstractBase)
class AbstractMultiConnectionProcessConnectionSelector(object):
    """ A connection selector for multi-connection processes
    """
    __slots__ = []

    # connections will be used when worked out how

    @abstractmethod
    def __init__(self, connections):
        """
        :param connections: The connections to be used
        """

    @abstractmethod
    def get_next_connection(self, message):
        """ Get the index of the  next connection for the process from a list\
            of connections.

        :param message: The SCP message to be sent
        :rtype: int
        """
