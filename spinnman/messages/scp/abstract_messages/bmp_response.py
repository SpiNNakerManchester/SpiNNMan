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

from logging import getLogger
from typing import Generic, Optional, TypeVar, final
from spinn_utilities.abstract_base import abstractmethod
from spinn_utilities.log import FormatAdapter
from spinn_utilities.overrides import overrides
from spinnman.messages.scp.enums import SCPCommand, SCPResult
from spinnman.exceptions import SpinnmanUnexpectedResponseCodeException
from .scp_response import AbstractSCPResponse

logger = FormatAdapter(getLogger(__name__))
#: :meta private:
T = TypeVar("T")


class BMPResponse(AbstractSCPResponse, Generic[T]):
    """
    Represents an SCP response that's tailored for the BMP connection.
    """
    __slots__ = ("__operation", "__command", "__value")

    def __init__(self, operation: str, command: SCPCommand):
        """
        :param operation: Operation name
        :param command: Command used for which this is the response
        """
        super().__init__()
        self.__operation = operation
        self.__command = command
        self.__value: Optional[T] = None

    @property
    def _value(self) -> T:
        """
        The value parsed from the message. Subclasses have to expose this to
        make the parsed payload visible.
        """
        if self.__value is None:
            raise ValueError("no value parsed yet")
        return self.__value

    @overrides(AbstractSCPResponse.read_data_bytestring)
    def read_data_bytestring(self, data: bytes, offset: int) -> None:
        result = self.scp_response_header.result
        if result != SCPResult.RC_OK:
            raise SpinnmanUnexpectedResponseCodeException(
                self.__operation, self.__command.name, result.name)
        self.__value = self._parse_payload(data, offset)

    @abstractmethod
    def _parse_payload(self, data: bytes, offset: int) -> T:
        """
        Parse the payload of the message. The header will already be OK.

        :param data:
            The full content of the message
        :param offset:
            Where the payload should start in the message
        :return:
            The parsed payload
        """
        raise NotImplementedError


@final
class BMPOKResponse(BMPResponse[None]):
    """
    A BMP response without payload to parse.
    """
    @abstractmethod
    def _parse_payload(self, data: bytes, offset: int) -> None:
        if len(data) != offset:
            logger.warning("response message with unexpected extra {} bytes",
                           len(data) - offset)
        return None

    @property
    def _value(self) -> None:
        # Override to remove None check; this is always None
        return None
