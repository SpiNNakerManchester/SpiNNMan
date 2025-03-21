# Copyright (c) 2025 The University of Manchester
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
from typing import List

from spinn_utilities.progress_bar import ProgressBar
from spinn_utilities.typing.coords import XY

from spinnman.processes.abstract_multi_connection_process import (
    AbstractMultiConnectionProcess)
from spinnman.messages.scp.impl.check_ok_response import CheckOKResponse
from spinnman.messages.scp.impl import RouterClear


class ClearRoutesProcess(AbstractMultiConnectionProcess[CheckOKResponse]):
    """ A Process to clear routes
    """

    def clear_routes(self, chips: List[XY]) -> None:
        """ Clear the routes on the selected chips

        :param chips: A list of x, y, address and value to set
        :raise SpinnmanIOException:
            If there is an error communicating with the board
        :raise SpinnmanInvalidPacketException:
            If a packet is received that is not in the valid format
        :raise SpinnmanInvalidParameterException:
            If x, y, p does not identify a valid processor
        :raise SpinnmanUnexpectedResponseCodeException:
            If a response indicates an error during the exchange
        """
        progress = ProgressBar(len(chips), "Clearing Multicast Routes")
        for x, y in progress.over(chips):
            self._send_request(RouterClear(x, y))
        self._finish()
        self.check_for_error()
        progress.end()
