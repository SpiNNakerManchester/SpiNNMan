# Copyright (c) 2014 The University of Manchester
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

import socket
from spinnman.model import BMPConnectionData
from spinnman.messages.scp.impl import IPTagSet
from spinnman.messages.sdp import SDPMessage, SDPHeader, SDPFlag
from spinnman.constants import SCP_SCAMP_PORT, CPU_INFO_BYTES, CPU_INFO_OFFSET
from spinnman.connections.udp_packet_connections import (
    SCAMPConnection, UDPConnection)
from spinnman.connections.udp_packet_connections.utils import (
    update_sdp_header_for_udp_send)
from spinnman.exceptions import SpinnmanTimeoutException


def work_out_bmp_from_machine_details(hostname, number_of_boards):
    """
    Work out the BMP connection IP address given the machine details.
    This is assumed to be the IP address of the machine, with 1 subtracted
    from the final part e.g. if the machine IP address is 192.168.0.5, the
    BMP IP address is assumed to be 192.168.0.4

    :param str hostname: the SpiNNaker machine main hostname or IP address
    :param int number_of_boards: the number of boards in the machine
    :return: The BMP connection data
    :rtype: BMPConnectionData
    """
    # take the IP address, split by dots, and subtract 1 off last bit
    ip_bits = socket.gethostbyname(hostname).split(".")
    ip_bits[-1] = str(int(ip_bits[-1]) - 1)
    bmp_ip_address = ".".join(ip_bits)

    # add board scope for each split
    # if None, the end user didn't enter anything, so assume one board
    # starting at position 0
    if number_of_boards == 0 or number_of_boards is None:
        board_range = [0]
    else:
        board_range = range(number_of_boards)

    # Assume a single board with no cabinet or frame specified
    return BMPConnectionData(cabinet=0, frame=0, ip_address=bmp_ip_address,
                             boards=board_range, port_num=SCP_SCAMP_PORT)


def get_vcpu_address(p):
    """
    Get the address of the vcpu_t structure for the given core.

    :param int p: The core
    :rtype: int
    """
    return CPU_INFO_OFFSET + (CPU_INFO_BYTES * p)


def send_port_trigger_message(connection, board_address):
    """
    Sends a port trigger message using a connection to (hopefully) open a
    port in a NAT and/or firewall to allow incoming packets to be received.

    :param UDPConnection connection:
        The UDP connection down which the trigger message should be sent
    :param str board_address:
        The IP address of the SpiNNaker board to which the message should be
        sent
    """

    # Set up the message so that no reply is expected and it is sent to an
    # invalid port for SCAMP.  The current version of SCAMP will reject
    # this message, but then fail to send a response since the
    # REPLY_NOT_EXPECTED flag is set (see scamp-3.c line 728 and 625-644)
    trigger_message = SDPMessage(SDPHeader(
        flags=SDPFlag.REPLY_NOT_EXPECTED, tag=0, destination_port=3,
        destination_cpu=0, destination_chip_x=0, destination_chip_y=0))
    update_sdp_header_for_udp_send(trigger_message.sdp_header, 0, 0)
    connection.send_to(
        trigger_message.bytestring, (board_address, SCP_SCAMP_PORT))


def reprogram_tag(connection: SCAMPConnection, tag: int, strip: bool = True):
    """
    Reprogram an IP Tag to send responses to a given SCAMPConnection.

    :param SCAMPConnection connection: The connection to target the tag at
    :param int tag: The id of the tag to set
    :param bool strip:
        True if the tag should strip SDP headers from outgoing messages
    :raises SpinnmanTimeoutException:
        If things time out several times
    """
    request = IPTagSet(
        connection.chip_x, connection.chip_y, [0, 0, 0, 0], 0, tag,
        strip=strip, use_sender=True)
    data = connection.get_scp_data(request)
    exn = None
    for _ in range(3):
        try:
            connection.send(data)
            _, _, response, offset = connection.receive_scp_response()
            request.get_scp_response().read_bytestring(response, offset)
            return
        except SpinnmanTimeoutException as e:
            exn = e
    # Should be impossible to get here with exn=None
    raise exn or Exception


def reprogram_tag_to_listener(
        connection: UDPConnection, x: int, y: int, ip_address: str, tag: int,
        strip: bool = True, read_response: bool = True):
    """
    Reprogram an IP Tag to send responses to a given connection that is
    not connected to a specific board. Such connections are normally
    receive-only connections.

    :param UDPConnection connection: The connection to target the tag at
    :param int x:
        The X coordinate of the Ethernet-enabled chip that should send to the
        connection
    :param int y:
        The Y coordinate of the Ethernet-enabled chip that should send to the
        connection
    :param str ip_address:
        The IP address of the Ethernet-enabled chip that should be given the
        message
    :param int tag: The id of the tag to set
    :param bool strip:
        True if the tag should strip SDP headers from outgoing messages
    :param bool read_response:
        True if the response to the reprogramming should be read
    :raises SpinnmanTimeoutException:
        If things time out several times
    """
    request = IPTagSet(
        x, y, [0, 0, 0, 0], 0, tag,
        strip=strip, use_sender=True)
    update_sdp_header_for_udp_send(request.sdp_header, x, y)
    send_data = b'\0\0' + request.bytestring
    exn = None
    for _ in range(3):
        try:
            connection.send_to(send_data, (ip_address, SCP_SCAMP_PORT))
            if read_response:
                request.get_scp_response().read_bytestring(
                    connection.receive(), 2)
            return
        except SpinnmanTimeoutException as e:
            exn = e
    # Should be impossible to get here with exn=None
    raise exn or Exception
