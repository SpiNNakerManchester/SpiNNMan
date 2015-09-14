"""
utility file which contains a lot of byte array reading and writing with
offsets as well as boot size calculations
"""

# spinnman imports
from spinnman import exceptions
from spinnman.model.bmp_connection_data import BMPConnectionData
from spinnman.messages.spinnaker_boot._system_variables import \
    _system_variable_boot_values

# spinnmachine imports
from spinn_machine.utilities import utilities

# general imports
import math
import socket
from spinnman.model.machine_dimensions import MachineDimensions


def _get_int_from_big_endian_bytearray(array, offset):
    """ Get an int from a byte array, using big-endian representation,\
        starting at the given offset

    :param array: The byte array to get the int from
    :type array: bytearray
    :param offset: The offset at which to start looking
    :type offset: int
    :return: The decoded integer
    :rtype: int
    """
    return ((array[offset] << 24) | (array[offset + 1] << 16) |
            (array[offset + 2] << 8) | array[offset + 3])


def _get_short_from_big_endian_bytearray(array, offset):
    """ Get a short from a byte array, using big-endian representation,
        starting at the given offset

    :param array: The byte array to get the short from
    :type array: bytearray
    :param offset: The offset at which to start looking
    :type offset: int
    :return: The decoded short
    :rtype: int
    """
    return (array[offset] << 8) | array[offset + 1]


def put_int_in_big_endian_byte_array(array, offset, value):
    """ Put an int in to a byte array, using big-endian representation,\
        starting at the given offset

    :param array: The byte array to put the int into
    :type array: bytearray
    :param offset: The offset in to the byte array at which to start the int
    :type offset: int
    :param value: The value to put in to the array
    :type value: int
    :return: Nothing is returned
    :rtype: None
    """
    array[offset] = (value >> 24) & 0xFF
    array[offset + 1] = (value >> 16) & 0xFF
    array[offset + 2] = (value >> 8) & 0xFF
    array[offset + 3] = value & 0xFF


def _put_short_in_big_endian_byte_array(array, offset, value):
    """ Put an int in to a byte array using big-endian representation,\
        starting at the given offset

    :param array: The byte array to put the int into
    :type array: bytearray
    :param offset: The offset in to the byte array at which to start the int
    :type offset: int
    :param value: The value to put in to the array
    :type value: int
    :return: Nothing is returned
    :rtype: None
    """
    array[offset] = (value >> 8) & 0xFF
    array[offset + 1] = value & 0xFF


def get_int_from_little_endian_bytearray(array, offset):
    """ Get an int from a byte array, using little-endian representation,\
        starting at the given offset

    :param array: The byte array to get the int from
    :type array: bytearray
    :param offset: The offset at which to start looking
    :type offset: int
    :return: The decoded integer
    :rtype: int
    """
    return ((array[offset + 3] << 24) | (array[offset + 2] << 16) |
            (array[offset + 1] << 8) | array[offset])


def get_short_from_little_endian_bytearray(array, offset):
    """ Get a short from a byte array, using little-endian representation,
        starting at the given offset

    :param array: The byte array to get the short from
    :type array: bytearray
    :param offset: The offset at which to start looking
    :type offset: int
    :return: The decoded short
    :rtype: int
    """
    return (array[offset + 1] << 8) | array[offset]


def _put_int_in_little_endian_byte_array(array, offset, value):
    """ Put an int in to a byte array, using little-endian representation,\
        starting at the given offset

    :param array: The byte array to put the int into
    :type array: bytearray
    :param offset: The offset in to the byte array at which to start the int
    :type offset: int
    :param value: The value to put in to the array
    :type value: int
    :return: Nothing is returned
    :rtype: None
    """
    array[offset + 3] = (value >> 24) & 0xFF
    array[offset + 2] = (value >> 16) & 0xFF
    array[offset + 1] = (value >> 8) & 0xFF
    array[offset] = value & 0xFF


def _put_short_in_little_endian_byte_array(array, offset, value):
    """ Put an int in to a byte array using big-endian representation,\
        starting at the given offset

    :param array: The byte array to put the int into
    :type array: bytearray
    :param offset: The offset in to the byte array at which to start the int
    :type offset: int
    :param value: The value to put in to the array
    :type value: int
    :return: Nothing is returned
    :rtype: None
    """
    array[offset + 1] = (value >> 8) & 0xFF
    array[offset] = value & 0xFF


def get_ideal_size(number_of_boards, version):
    """ Get the ideal width and height of the machine when no dimensions are\
        given - assumes the machine is square, otherwise it is wider than it\
        is tall

    :param number_of_boards: the number of boards used within the machine
    :param version: the board version being used
    :return: The MachineDimensions
    :rtype: :py:class:`spinnman.model.machine_dimensions.MachineDimensions`
    """

    if number_of_boards == 1:
        return _system_variable_boot_values.\
            spinnaker_standard_board_to_machine_sizes[version]
    elif version == 4 or version == 5:
        if number_of_boards % 3 != 0:
            raise exceptions.SpinnmanInvalidParameterException(
                "number_of_boards", number_of_boards,
                "Not a multiple of 3")

        # Special case to avoid division by 0
        if number_of_boards == 0:
            return MachineDimensions(0, 0)

        # Find the largest pair of factors to discover the squarest system
        h = 0
        for h in reversed(range(1, int(math.sqrt(number_of_boards // 3)) + 1)):
            if (number_of_boards // 3) % h == 0:
                break
        w = (number_of_boards // 3) // h

        # convert from triads to chip size
        return MachineDimensions(w * 12, h * 12)
    else:
        raise exceptions.SpinnmanInvalidParameterException(
            "version", version, "unrecognized board version for "
                                "default sizes above 1 board")


def locate_middle_chips_to_query(width, height, invalid_chips):
    """ Locate the middle set of chips on the board, given chips that have\
        been manually removed

    :param width: the width of the machine in chips
    :param height: the height of the machine in chips
    :param invalid_chips: the list of chips that are down
    :return: a list of chips to query
    """
    middle_chip_x = int(round(width / 2))
    middle_chip_y = int(round(height / 2))
    return utilities.get_closest_chips_to(
        middle_chip_x, middle_chip_y, width - 1, height - 1, invalid_chips)


def work_out_bmp_from_machine_details(hostname, number_of_boards):
    """ Work out the BMP connection ip address given the machine details.\
        This is assumed to be the IP address of the machine, with 1 subtracted\
        from the final part e.g. if the machine IP address is 192.168.0.1, the\
        BMP IP address is assumed to be 192.168.0.0

    :param hostname: the spinnaker machine main hostname or IP address
    :param number_of_boards: the number of boards in the machine
    :return: The BMP connection data
    """
    # take the ipaddress, split by dots, and subtract 1 off last bit
    ipstring = socket.gethostbyname(hostname)
    ip_string_bits = ipstring.split(".")
    ip_string_bits[len(ip_string_bits) - 1] = str(int(
        ip_string_bits[len(ip_string_bits) - 1]) - 1)
    bmp_ip_address = ".".join(ip_string_bits)

    # add board scope for each split
    # if None, the end user didnt enter anything, so assume one board
    # starting at position 0
    board_range = list()
    if number_of_boards == 0 or number_of_boards is None:
        board_range.append(int(0))
    else:
        for board_value in range(number_of_boards):
            board_range.append(int(board_value))

    # Assume a single board with no cabinet or frame specified
    return BMPConnectionData(cabinet=0, frame=0, ip_address=bmp_ip_address,
                             boards=board_range)


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
