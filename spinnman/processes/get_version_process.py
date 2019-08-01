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

from spinnman.messages.scp.impl import GetVersion
from .abstract_single_connection_process import AbstractSingleConnectionProcess
from spinnman.constants import N_RETRIES


class GetVersionProcess(AbstractSingleConnectionProcess):
    """ A process for getting the version of the machine.
    """
    __slots__ = [
        "_version_info"]

    def __init__(self, connection_selector, n_retries=N_RETRIES):
        super(GetVersionProcess, self).__init__(connection_selector, n_retries)
        self._version_info = None

    def _get_response(self, version_response):
        self._version_info = version_response.version_info

    def get_version(self, x, y, p):
        self._send_request(GetVersion(x=x, y=y, p=p),
                           self._get_response)
        self._finish()

        self.check_for_error()
        return self._version_info
