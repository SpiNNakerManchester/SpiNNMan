# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from spinn_utilities.abstract_base import AbstractBase, abstractmethod
from spinn_utilities.abstract_context_manager import AbstractContextManager


class Connection(AbstractContextManager, metaclass=AbstractBase):
    """
    An abstract connection to the SpiNNaker board over some medium.
    """

    __slots__ = ()

    @abstractmethod
    def is_connected(self):
        """
        Determines if the medium is connected at this point in time.

        :return: True if the medium is connected, False otherwise
        :rtype: bool
        :raise SpinnmanIOException:
            If there is an error when determining the connectivity of the
            medium.
        """

    @abstractmethod
    def close(self):
        """
        Closes the connection.
        """
