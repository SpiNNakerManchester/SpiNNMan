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

_SDP_SOURCE_PORT = 7
_SDP_SOURCE_CPU = 31
_SDP_TAG = 0xFF


def update_sdp_header_for_udp_send(sdp_header, source_x, source_y):
    """ Apply defaults to the SDP header for sending over UDP

    :param SDPHeader sdp_header: The SDP header values
    """
    sdp_header.tag = _SDP_TAG
    sdp_header.source_port = _SDP_SOURCE_PORT
    sdp_header.source_cpu = _SDP_SOURCE_CPU
    sdp_header.source_chip_x = source_x
    sdp_header.source_chip_y = source_y
