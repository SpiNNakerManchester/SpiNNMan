"""
utility file which contains a lot of byte array reading and writing with offsets
as well as boot size calculations
"""

# spinnman imports
from spinnman import exceptions
from spinnman.data.bmp_connection_data import BMPConnectionData
from spinnman.messages.spinnaker_boot._system_variables import \
    _system_variable_boot_values

#general imports
import math
import socket


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


def get_idead_size(number_of_boards, version):
    """
    returns the width and height of the machine when no dimensions are used
    :param number_of_boards: the number of boards used within the machine
    :param version: the board version being used
    :return: a dictory with x and y keys.
    """

    if number_of_boards == 1:
        return _system_variable_boot_values.\
            spinnaker_standard_board_to_machine_sizes[version]
    elif version == 4 or version == 5:
        # fixme this could be a call to spinner, but would require spinny to be installed which requires multiple end user installs
        if number_of_boards % 3 != 0:
            raise exceptions.SpinnmanInvalidParameterException(
                "number_of_boards", number_of_boards,
                "{} is not a multiple of 3".format(number_of_boards))
        # Special case to avoid division by 0
        if number_of_boards == 0:
            return {'x': 0, 'y': 0}
        # Find the largest pair of factors to discover the squarest system
        for h in reversed(range(1, int(math.sqrt(number_of_boards // 3)) + 1)):  # pragma: no branch
            if (number_of_boards // 3) % h == 0:
                break
            w = (number_of_boards // 3) // h
            return {'x': w, 'y': h}
    else:
        raise exceptions.SpinnmanInvalidParameterException(
            "version", version, "{} is not a understandable board type for "
                                "default sizes above 1 board".format(version))


def sort_out_bmp_string(bmp_string):
    """
    takes a bmp line and splits it into ipaddress and a int for board scope
    where each bit in the int states if the board is to be used in the scope
    :param bmp_string: the bmp string to be converted
    :return: the bmp ipaddress and the boards scope int
    """
    bmp_string_split = bmp_string.split("/")
    # if there is no split, then assume its one board, located at position 0
    if len(bmp_string_split) == 1:
        # verify that theres no cabinate and frame defs
        bmp_string_split = bmp_string.split(";")
        if len(bmp_string_split) == 1:
            return BMPConnectionData(0, 0, bmp_string, 0)
    else:
        cabinate_frame_ip_address = bmp_string_split[0].split(";")
        # if no cabinate or frame, assume they are 0 0
        if len(cabinate_frame_ip_address) == 1:
            cabinate = 0
            frame = 0
            ip_address = cabinate_frame_ip_address[0]
        else:
            cabinate = cabinate_frame_ip_address[0]
            frame = cabinate_frame_ip_address[1]
            ip_address = cabinate_frame_ip_address[2]

        # try splitting by - first
        board_scope_split = bmp_string_split[1].split("-")
        if len(board_scope_split) == 1:
            # assume seperated by , instead
            board_scope_split = bmp_string_split[1].split(",")
        else:
            # get range into same format as list, for ease later
            new_values = list()
            for value in range(int(board_scope_split[0]),
                               int(board_scope_split[1])):
                new_values.append(value)

        # add board scope for each split
        board_int = list()
        for board_value in board_scope_split:
            board_int.append(int(board_value))

        return BMPConnectionData(cabinate, frame, ip_address, board_int)


def update_mappers(
        bmp_to_data_mapping, cabinat_frame_to_connection_mapping,
        bmp_connection_data, udp_bmp_connection):
    """
    helper method for the transciever for updating data struct with connection
    :param bmp_to_data_mapping: the connection to connection data mapper
    :param cabinat_frame_to_connection_mapping: the cab frame to connection
    mapper
    :param bmp_connection_data: the connection data object
    :param udp_bmp_connection: the bmp connection
    :return: None
    """
    # update data mapper
    bmp_to_data_mapping[udp_bmp_connection] = bmp_connection_data
    # update cab frame mapper
    cabinat_frame_to_connection_mapping[
        (bmp_connection_data.cabinate,
         bmp_connection_data.frame)] = udp_bmp_connection


def sort_out_bmp_from_machine(hostname, number_of_boards):
    """

    :param hostname: the spinnaker machines ipaddress
    :param number_of_boards: the number of boards this machine is expected to
    be built out of
    :return:the bmp ipaddress and the boards scope as a iterable of ints
    """
    # take the ipaddress, split by dots, and subtract 1 off last bit
    ipstring = socket.gethostbyname(hostname)
    ip_string_bits = ipstring.split(".")
    # subtract one off the last bit of the ip address
    ip_string_bits[len(ip_string_bits) - 1] = \
        str(int(ip_string_bits[len(ip_string_bits) - 1]) - 1)
    bmp_ip_address = ".".join(ip_string_bits)
    # add board scope for each split
    board_int = list()
    for board_value in range(number_of_boards):
        board_int.append(int(board_value))
    return bmp_ip_address, board_int
