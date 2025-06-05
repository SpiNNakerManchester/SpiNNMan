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

from spinn_machine.core_subsets import CoreSubsets
from spinnman.messages.scp.impl import ApplicationRun, CheckOKResponse
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class ApplicationRunProcess(AbstractMultiConnectionProcess[CheckOKResponse]):
    """
    A process to run an application.
    """
    __slots__ = ()

    def run(self, app_id: int, core_subsets: CoreSubsets, wait: bool) -> None:
        """
        Runs the application.

        :param app_id:
        :param core_subsets:
        :param wait:
`        """
        with self._collect_responses():
            for core_subset in core_subsets:
                self._send_request(ApplicationRun(
                    app_id, core_subset.x, core_subset.y,
                    core_subset.processor_ids, wait))
