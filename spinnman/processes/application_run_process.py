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

from spinnman.messages.scp.impl import ApplicationRun
from .abstract_multi_connection_process import AbstractMultiConnectionProcess


class ApplicationRunProcess(AbstractMultiConnectionProcess):
    __slots__ = []

    def run(self, app_id, core_subsets, wait):
        for core_subset in core_subsets:
            x = core_subset.x
            y = core_subset.y
            self._send_request(
                ApplicationRun(
                    app_id, x, y, core_subset.processor_ids, wait))
        self._finish()
        self.check_for_error()
