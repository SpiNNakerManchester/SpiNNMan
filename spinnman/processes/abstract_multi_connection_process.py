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

from six import itervalues
from .abstract_process import AbstractProcess
from spinnman.connections import SCPRequestPipeLine
from spinnman.constants import SCP_TIMEOUT, N_RETRIES


class AbstractMultiConnectionProcess(AbstractProcess):
    """ A process that uses multiple connections in communication.
    """
    __slots__ = [
        "_intermediate_channel_waits",
        "_n_channels",
        "_n_retries",
        "_next_connection_selector",
        "_scp_request_pipelines",
        "_timeout"]

    def __init__(self, next_connection_selector,
                 n_retries=N_RETRIES, timeout=SCP_TIMEOUT, n_channels=8,
                 intermediate_channel_waits=7):
        super(AbstractMultiConnectionProcess, self).__init__()
        self._scp_request_pipelines = dict()
        self._n_retries = n_retries
        self._timeout = timeout
        self._n_channels = n_channels
        self._intermediate_channel_waits = intermediate_channel_waits
        self._next_connection_selector = next_connection_selector

    def _send_request(self, request, callback=None, error_callback=None):
        if error_callback is None:
            error_callback = self._receive_error
        connection = self._next_connection_selector.get_next_connection(
            request)
        if connection not in self._scp_request_pipelines:
            scp_request_set = SCPRequestPipeLine(
                connection, n_retries=self._n_retries,
                packet_timeout=self._timeout,
                n_channels=self._n_channels,
                intermediate_channel_waits=self._intermediate_channel_waits)
            self._scp_request_pipelines[connection] = scp_request_set
        self._scp_request_pipelines[connection].send_request(
            request, callback, error_callback)

    def _finish(self):
        for request_pipeline in itervalues(self._scp_request_pipelines):
            request_pipeline.finish()
