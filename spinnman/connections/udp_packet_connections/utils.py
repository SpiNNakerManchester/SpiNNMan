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

_SDP_SOURCE_PORT = 7
_SDP_SOURCE_CPU = 31
_SDP_TAG = 0xFF


def update_sdp_header_for_udp_send(sdp_header, source_x, source_y):
    """
    Apply defaults to the SDP header for sending over UDP.

    :param SDPHeader sdp_header: The SDP header values
    """
    sdp_header.tag = _SDP_TAG
    sdp_header.source_port = _SDP_SOURCE_PORT
    sdp_header.source_cpu = _SDP_SOURCE_CPU
    sdp_header.source_chip_x = source_x
    sdp_header.source_chip_y = source_y
