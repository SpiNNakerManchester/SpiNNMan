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
from spinn_utilities.abstract_context_manager import AbstractContextManager


class Connection(AbstractContextManager, metaclass=AbstractBase):
    """ An abstract connection to the SpiNNaker board over some medium
    """

    __slots__ = ()

    @abstractmethod
    def is_connected(self):
        """ Determines if the medium is connected at this point in time

        :return: True if the medium is connected, False otherwise
        :rtype: bool
        :raise SpinnmanIOException:
            If there is an error when determining the connectivity of the
            medium.
        """

    @abstractmethod
    def close(self):
        """ Closes the connection
        """
