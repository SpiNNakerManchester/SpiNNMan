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

from .abstract_multi_connection_process import AbstractMultiConnectionProcess
from spinnman.constants import SCP_TIMEOUT


class SendSingleCommandProcess(AbstractMultiConnectionProcess):
    __slots__ = [
        "_response"]

    def __init__(self, connection_selector, n_retries=3, timeout=SCP_TIMEOUT):
        super(SendSingleCommandProcess, self).__init__(
            connection_selector, n_retries=n_retries, timeout=timeout)
        self._response = None

    def handle_response(self, response):
        self._response = response

    def execute(self, request):
        self._send_request(request, self.handle_response)
        self._finish()
        self.check_for_error()
        return self._response
