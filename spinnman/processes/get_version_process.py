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

from typing import Optional

from spinnman.messages.scp.impl import GetVersion
from spinnman.constants import N_RETRIES
from spinnman.model import VersionInfo
from spinnman.messages.scp.impl.get_version_response import GetVersionResponse

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from .abstract_multi_connection_process_connection_selector import (
    ConnectionSelector)


class GetVersionProcess(AbstractMultiConnectionProcess[GetVersionResponse]):
    """
    A process for getting the version of the machine.
    """
    __slots__ = "_version_info",

    def __init__(self, connection_selector: ConnectionSelector,
                 n_retries: int = N_RETRIES):
        """
        :param connection_selector:
        """
        super().__init__(connection_selector, n_retries)
        self._version_info: Optional[VersionInfo] = None

    def _get_response(self, version_response: GetVersionResponse) -> None:
        self._version_info = version_response.version_info

    def get_version(self, x: int, y: int, p: int) -> VersionInfo:
        """
        :param x:
        :param y:
        :param p:
        :returns: SC&MP/SARK version information
        """
        with self._collect_responses():
            self._send_request(GetVersion(x=x, y=y, p=p), self._get_response)
        assert self._version_info is not None
        return self._version_info
