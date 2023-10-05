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

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import SCP_TIMEOUT


class SendSingleCommandProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_response"]

    def __init__(self, connection_selector, n_retries=3, timeout=SCP_TIMEOUT):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(
            connection_selector, n_retries=n_retries, timeout=timeout)
        self._response = None

    def __handle_response(self, response):
        self._response = response

    def execute(self, request):
        """
        :param AbstractSCPRequest request:
        :rtype: AbstractSCPResponse
        """
        self._send_request(request, self.__handle_response)
        self._finish()
        self.check_for_error()
        return self._response
