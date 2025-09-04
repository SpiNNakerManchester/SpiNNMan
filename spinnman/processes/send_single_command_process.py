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

from typing import Generic, Optional, TypeVar, Set

from spinnman.constants import SCP_TIMEOUT

from spinnman.messages.scp.abstract_messages import AbstractSCPResponse
from spinnman.messages.scp.abstract_messages import AbstractSCPRequest
from spinnman.messages.scp.enums.scp_result import SCPResult

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)
#: Type of responses.
#: :meta private:
R = TypeVar("R", bound=AbstractSCPResponse)


class SendSingleCommandProcess(AbstractMultiConnectionProcess, Generic[R]):
    """
    A process that sends a single command and waits for a simple response.
    """
    __slots__ = ("_response", )

    def __init__(self, connection_selector: ConnectionSelector,
                 n_retries: int = 3, timeout: float = SCP_TIMEOUT,
                 non_fail_retry_codes: Optional[Set[SCPResult]] = None):
        """
        :param connection_selector:
        :param n_retries:
            The number of retries of a message to use. Passed to
            :py:class:`SCPRequestPipeLine`
        :param timeout:
            The timeout, in seconds. Passed to
            :py:class:`SCPRequestPipeLine`
        :param non_fail_retry_codes:
            Optional set of responses that result in retry but after retrying
            don't then result in failure even if returned on the last call.
        """
        super().__init__(
            connection_selector, n_retries=n_retries, timeout=timeout,
            non_fail_retry_codes=non_fail_retry_codes)
        self._response: Optional[R] = None

    def __handle_response(self, response: R) -> None:
        self._response = response

    def execute(self, request: AbstractSCPRequest[R]) -> R:
        """
        :param request:
        :returns: The response from this request.
        """
        with self._collect_responses():
            self._send_request(request, self.__handle_response)
        assert self._response is not None
        return self._response
