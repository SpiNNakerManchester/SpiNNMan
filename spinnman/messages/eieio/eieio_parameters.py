from abc import ABCMeta
from spinnman.messages.eieio.eieio_prefix import EIEIOPrefix
from spynnaker.pyNN import exceptions

"""
                 port, board_address=None, tag=None, key_prefix=None, 
                 prefix_type=None,

                 virtual_key=None, check_key=True, key_left_shift=0,
                 sdp_port=1, buffer_space=0, notify_buffer_space=False,
                 space_before_notification=0, notification_tag=None,
                 notification_ip_address=None, notification_port=None,
                 notification_strip_sdp=True

                 ip_address, strip_sdp=True, use_prefix=False,
                 message_type=EIEIOType.KEY_32_BIT, right_shift=0, 
                 payload_as_time_stamps=True, use_payload_prefix=True, 
                 payload_prefix=None, payload_right_shift=0,
                 number_of_packets_sent_per_time_step=0

"""

class EIEIOParameters(object):
    def __init__(self, port, ip_address=None, board=None, tag=None,
                 key_prefix=None, prefix_type=None):
                 
        self._port = port
        self._ip_address = ip_address
        self._tag = tag
        self._board = board
        if key_prefix is not None and prefix_type is None:
           raise exceptions.ConfigurationException(
               "To use a prefix, you must declare in which position to use the "
               "prefix with the prefix_type parameter.")
        else:
           self._key_prefix = key_prefix
        if (prefix_type == "UPPER" or
            prefix_type == "UPPER_HALF_WORD" or 
            prefix_type == EIEIOPrefix.UPPER_HALF_WORD):
           self._prefix_type = EIEIOPrefix.UPPER_HALF_WORD
        elif (prefix_type == "LOWER" or
              prefix_type == "LOWER_HALF_WORD" or 
              prefix_type == EIEIOPrefix.LOWER_HALF_WORD):
           self._prefix_type = EIEIOPrefix.LOWER_HALF_WORD
        elif prefix_type is None:
           self._prefix_type = None
        else:
           raise exceptions.ConfigurationException(
                 "Unsupported prefix type: %s. Valid types are "
                 "UPPER[_HALF_WORD], LOWER[_HALF_WORD]" % prefix_type)
        if self._key_prefix is None:
           self._use_prefix = False
        else:
           self._use_prefix = True

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        self._tag = tag

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, port):
        self._port = port

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter     
    def ip_address(self, ip_address):
        self._ip_address = ip_address

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board):
        self._board = board

    @property
    def key_prefix(self):
        return self._key_prefix

    @key_prefix.setter
    def key_prefix(self, key_prefix):
        self._key_prefix = key_prefix
        if key_prefix is not None:
           self._use_prefix = True

    @property
    def use_prefix(self):
        return self._use_prefix

    @property
    def prefix_type(self):
        return self._prefix_type
  
    @prefix_type.setter
    def prefix_type(self, prefix_type):
        self._prefix_type = prefix_type
