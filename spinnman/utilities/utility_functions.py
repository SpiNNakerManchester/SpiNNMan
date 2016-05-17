
# spinnman imports
from spinnman.model.bmp_connection_data import BMPConnectionData
from spinnman import constants

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


def get_router_timeout_value(mantissa, exponent):
    """ Get the timeout value of a router in ticks, given the mantissa and\
        exponent of the value

    :param mantissa: The mantissa of the value, between 0 and 15
    :type mantissa: int
    :param exponent: The exponent of the value, between 0 and 15
    :type exponent: int
    """
    if exponent <= 4:
        return ((mantissa + 16) - (2 ** (4 - exponent))) * (2 ** exponent)
    return (mantissa + 16) * (2 ** exponent)


def get_router_timeout_value_from_byte(value):
    """ Get the timeout value of a router in ticks, given an 8-bit floating\
        point value stored in an int(!)

    :param value: The value to convert
    :type value: int
    """
    return get_router_timeout_value(value & 0xF, (value >> 4) & 0XF)


def get_vcpu_address(p):
    """ Get the address of the vcpu_t structure for the given core

    :param p: The core
    :type p: int
    """
    return constants.CPU_INFO_OFFSET + (constants.CPU_INFO_BYTES * p)
