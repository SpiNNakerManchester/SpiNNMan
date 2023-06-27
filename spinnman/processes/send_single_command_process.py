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
from typing import Generic, Optional, TypeVar
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import SCP_TIMEOUT
from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)
_R = TypeVar("_R", bound=AbstractSCPResponse)


class SendSingleCommandProcess(AbstractMultiConnectionProcess, Generic[_R]):
    """
    A process that sends a single command and waits for a simple response.
    """
    __slots__ = ("_response", )

    def __init__(self, connection_selector: ConnectionSelector,
                 n_retries: int = 3, timeout: float = SCP_TIMEOUT):
        """
        :param ConnectionSelector connection_selector:
        :param int n_retries:
            The number of retries of a message to use. Passed to
            :py:class:`SCPRequestPipeLine`
        :param float timeout:
            The timeout, in seconds. Passed to
            :py:class:`SCPRequestPipeLine`
        """
        super().__init__(
            connection_selector, n_retries=n_retries, timeout=timeout)
        self._response: Optional[_R] = None

    def __handle_response(self, response: _R):
        self._response = response

    def execute(self, request: AbstractSCPRequest[_R]) -> _R:
        """
        :param AbstractSCPRequest request:
        :rtype: AbstractSCPResponse
        """
        with self._collect_responses():
            self._send_request(request, self.__handle_response)
        assert self._response is not None
        return self._response
