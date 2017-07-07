# spinnman imports
from spinnman.model import BMPConnectionData
from spinnman import constants
from spinnman.messages.sdp import SDPMessage, SDPHeader, SDPFlag
from spinnman.connections.udp_packet_connections.utils \
    import update_sdp_header_for_udp_send

# general imports
import socket


def work_out_bmp_from_machine_details(hostname, number_of_boards):
    """ Work out the BMP connection ip address given the machine details.\
        This is assumed to be the IP address of the machine, with 1 subtracted\
        from the final part e.g. if the machine IP address is 192.168.0.1, the\
        BMP IP address is assumed to be 192.168.0.0

    :param hostname: the spinnaker machine main hostname or IP address
    :param number_of_boards: the number of boards in the machine
    :return: The BMP connection data
    """
    # take the ip address, split by dots, and subtract 1 off last bit
    ipstring = socket.gethostbyname(hostname)
    ip_string_bits = ipstring.split(".")
    ip_string_bits[len(ip_string_bits) - 1] = str(int(
        ip_string_bits[len(ip_string_bits) - 1]) - 1)
    bmp_ip_address_and_port = ".".join(ip_string_bits)
    bmp_bits = bmp_ip_address_and_port.split(",")
    if len(bmp_bits) == 1:
        bmp_ip_address = bmp_bits[0]
        bmp_port = None
    else:
        bmp_ip_address = bmp_bits[0]
        bmp_port = bmp_bits[1]

    # add board scope for each split
    # if None, the end user didn't enter anything, so assume one board
    # starting at position 0
    board_range = list()
    if number_of_boards == 0 or number_of_boards is None:
        board_range.append(int(0))
    else:
        for board_value in range(number_of_boards):
            board_range.append(int(board_value))

    # Assume a single board with no cabinet or frame specified
    return BMPConnectionData(cabinet=0, frame=0, ip_address=bmp_ip_address,
                             boards=board_range, port_num=int(bmp_port))


def get_vcpu_address(p):
    """ Get the address of the vcpu_t structure for the given core

    :param p: The core
    :type p: int
    """
    return constants.CPU_INFO_OFFSET + (constants.CPU_INFO_BYTES * p)


def send_port_trigger_message(connection, board_address):
    """Sends a port trigger message using a connection to (hopefully) open \
    a port in a NAT and/or firewall to allow incoming packets to be received.

    :param connection: The UDP connection down which the trigger message\
        should be sent
    :param board_address: The address of the SpiNNaker board to which the\
        message should be sent
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
        trigger_message.bytestring,
        (board_address, constants.SCP_SCAMP_PORT))
