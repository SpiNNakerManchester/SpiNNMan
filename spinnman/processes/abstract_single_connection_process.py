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

from .abstract_process import AbstractProcess
from spinnman.connections import SCPRequestPipeLine
from spinnman.constants import N_RETRIES


class AbstractSingleConnectionProcess(AbstractProcess):
    """ A process that uses a single connection in communication.
    """
    __slots__ = [
        "_connection_selector",
        "_scp_request_pipeline",
        "_n_retries"]

    def __init__(self, connection_selector, n_retries=N_RETRIES):
        super(AbstractSingleConnectionProcess, self).__init__()
        self._scp_request_pipeline = None
        self._connection_selector = connection_selector
        self._n_retries = n_retries

    def _send_request(self, request, callback=None, error_callback=None):
        if error_callback is None:
            error_callback = self._receive_error

        # If no pipe line built yet, build one on the connection selected for
        # it
        if self._scp_request_pipeline is None:
            self._scp_request_pipeline = SCPRequestPipeLine(
                self._connection_selector.get_next_connection(request),
                n_retries=self._n_retries)

        # send request
        self._scp_request_pipeline.send_request(
            request, callback, error_callback)

    def _finish(self):
        self._scp_request_pipeline.finish()
