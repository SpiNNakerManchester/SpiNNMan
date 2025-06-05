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

from spinnman.messages.sdp import SDPHeader


# Kept for spalloc_server to use
def update_sdp_header_for_udp_send(
        sdp_header: SDPHeader, source_x: int, source_y: int) -> None:
    """
    Apply defaults to the SDP header for sending over UDP.

    .. deprecated:: 7.0
        Use :py:meth:`SDPHeader.update_for_send` instead.

    :param sdp_header: The SDP header to update
    :param source_x: Where the packet is deemed to originate: X coordinate
    :param source_y: Where the packet is deemed to originate: Y coordinate
    """
    sdp_header.update_for_send(source_x, source_y)
