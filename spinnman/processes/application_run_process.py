# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
