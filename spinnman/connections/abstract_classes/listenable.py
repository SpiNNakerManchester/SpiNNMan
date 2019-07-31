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
class Listenable(object):

    __slots__ = ()

    @abstractmethod
    def get_receive_method(self):
        """ Get the method that receives for this connection
        """

    @abstractmethod
    def is_ready_to_receive(self, timeout=0):
        """ Determines if there is an SCP packet to be read without blocking

        :param timeout: \
            The time to wait before returning if the connection is not ready
        :type timeout: int
        :return: True if there is an SCP packet to be read
        :rtype: bool
        """
