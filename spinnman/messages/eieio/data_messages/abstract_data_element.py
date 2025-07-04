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
from spinnman.messages.eieio.eieio_type import EIEIOType


class AbstractDataElement(object, metaclass=AbstractBase):
    """
    A marker interface for possible data elements in the EIEIO data packet.
    """

    __slots__ = ()

    @abstractmethod
    def get_bytestring(self, eieio_type: EIEIOType) -> bytes:
        """
        Get a byte-string for the given type

        :param eieio_type: The type of the message being written
        :return: A byte-string for the element
        :raise SpinnmanInvalidParameterException:
            If the type is incompatible with the element
        """
        raise NotImplementedError
