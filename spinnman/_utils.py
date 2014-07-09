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

def _put_int_in_big_endian_byte_array(array, offset, value):
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

def _get_int_from_little_endian_bytearray(array, offset):
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

def _get_short_from_little_endian_bytearray(array, offset):
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
