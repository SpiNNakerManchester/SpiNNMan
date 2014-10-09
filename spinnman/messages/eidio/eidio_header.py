from spinnman.messages.eidio.eidio_type_param import EIDIOTypeParam
from spinnman import exceptions

class EIDIOHeader(object):

    def __init__(self, type_param, count_param, tag_param=0, prefix_param=None,
                 payload_base=None, prefix_type=None, is_time=False):
        """the basic eidio header

        :param prefix_param: the prefix if needed, or None
        :param payload_base: the data to replace the prefix if not prefix set/
         or None
        :param type_param: the type of message format
        :param count_param: the count param
        :param tag_param: the tag being used or 0
        :param prefix_type: the position of the prefix (upper or lower)
        :param is_time: is the time param set
        :type prefix_param: int or None
        :type payload_base: int or None
        :type type_param: spinnman.spinnman.messages.eidio.eidio_type_param.EIDIOTypeParam
        :type count_param: int
        :type tag_param: int
        :type prefix_type: spinnman.spinnman.messages.eidio.eidio_prefix_type
        :type is_time: bool
        :return:
        """
        self._prefix_param = prefix_param
        self._payload_base = payload_base
        if not isinstance(type_param, EIDIOTypeParam):
            raise exceptions.SpinnmanInvalidParameterException(
                "the eidio type_param is not a valid EIDIOTypeParam", "", "")
        self._type_param = type_param
        self._count_param = count_param
        self._tag_param = tag_param
        self._prefix_type = prefix_type
        self._is_time = is_time

    def write_eidio_header(self, byte_writer):
        data = 0
        # the flag for no prefix
        if self._prefix_param is not None:
            data |= 1 << 7  # the flag for prefix
        else:
            data |= 0 << 7  # the flag for prefix
        #the flag for packet format
        data |= 0 << 6
        #payload param
        if self._payload_base is not None:
            data |= 1 << 5  # the flag for payload prefix
        else:
            data |= 0 << 5  # the flag for payload prefix
        #time param
        if self._is_time:
            data |= 1 << 4  # the flag for time
        else:
            data |= 0 << 4  # the flag for time

        #type param
        data |= self._type_param.value << 2

        #tag param
        data |= self._tag_param
        byte_writer.write_byte(data)

        #count param
        byte_writer.write_byte(self._count_param)
