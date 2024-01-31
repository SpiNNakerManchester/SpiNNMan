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

from spinnman.messages.scp.impl import CountState
from spinnman.messages.scp.enums.scp_result import SCPResult
from .abstract_multi_connection_process import AbstractMultiConnectionProcess

# Timeout for getting core state count; higher due to more waiting needed
GET_CORE_COUNT_TIMEOUT = 2.0


class GetNCoresInStateProcess(AbstractMultiConnectionProcess):
    """
    Gets the state of a core over the provided connection.
    """
    __slots__ = [
        "_n_cores"]

    def __init__(self, connection_selector):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector, timeout=GET_CORE_COUNT_TIMEOUT,
                         non_fail_retry_codes={SCPResult.RC_P2P_NOREPLY})
        self._n_cores = 0

    def __handle_response(self, response):
        self._n_cores += response.count

    def get_n_cores_in_state(self, xys, app_id, state):
        """
        :param list(int,int) xys:
        :param int app_id:
        :param int state:
        :rtype: int
        """
        for c_x, c_y in xys:
            self._send_request(
                CountState(c_x, c_y, app_id, state), self.__handle_response)
        self._finish()
        self.check_for_error()

        return self._n_cores
