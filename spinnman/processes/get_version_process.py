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

from spinnman.messages.scp.impl import GetVersion
from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import N_RETRIES


class GetVersionProcess(AbstractMultiConnectionProcess):
    """
    A process for getting the version of the machine.
    """
    __slots__ = [
        "_version_info"]

    def __init__(self, connection_selector, n_retries=N_RETRIES):
        """
        :param connection_selector:
        :type connection_selector:
            AbstractMultiConnectionProcessConnectionSelector
        """
        super().__init__(connection_selector, n_retries)
        self._version_info = None

    def _get_response(self, version_response):
        """
        :param GetVersionResponse version_response:
        """
        self._version_info = version_response.version_info

    def get_version(self, x, y, p):
        """
        :param int x:
        :param int y:
        :param int p:
        :rtype: VersionInfo
        """
        self._send_request(GetVersion(x=x, y=y, p=p),
                           self._get_response)
        self._finish()

        self.check_for_error()
        return self._version_info
