# Copyright (c) 2015 The University of Manchester
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


# Should inherit from Connection, but doesn't for MRO reasons
class Listenable(object, metaclass=AbstractBase):
    """
    An interface for connections that can listen for incoming messages.

    Implementing this interface means that the connection can be used with
    :py:class:`ConnectionListener`.
    """

    __slots__ = ()

    @abstractmethod
    def get_receive_method(self):
        """
        Get the method that receives for this connection.
        """

    @abstractmethod
    def is_ready_to_receive(self, timeout=0):
        """
        Determines if there is an SCP packet to be read without blocking.

        :param int timeout:
            The time to wait before returning if the connection is not ready
        :return: True if there is an SCP packet to be read
        :rtype: bool
        """
