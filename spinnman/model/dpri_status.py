import struct

from spinnman.messages.scp.enums import DPRIFlags


def _decode_router_timeout_value(value):
    """ Get the timeout value of a router in ticks, given an 8-bit floating\
        point value stored in an int (!)

    :param value: The value to convert
    :type value: int
    """
    mantissa = value & 0xF
    exponent = (value >> 4) & 0xF
    if exponent <= 4:
        return ((mantissa + 16) - (2 ** (4 - exponent))) * (2 ** exponent)
    return (mantissa + 16) * (2 ** exponent)


class DPRIStatus(object):
    """ Represents a status information from dropped packet reinjection
    """

    def __init__(self, data, offset):
        """
        :param data: The data containing the information
        :type data: str
        :param offset: The offset in the data where the information starts
        :type offset: int
        """
        (self._router_timeout, self._router_emergency_timeout,
         self._n_dropped_packets, self._n_missed_dropped_packets,
         self._n_dropped_packet_overflows, self._n_reinjected_packets,
         self._n_link_dumps, self._n_processor_dumps,
         self._flags) = struct.unpack_from("<IIIIIIIII", data, offset)

    @property
    def router_timeout(self):
        """ The WAIT1 timeout value of the router in cycles
        """
        return _decode_router_timeout_value(self._router_timeout)

    @property
    def router_emergency_timeout(self):
        """ The WAIT2 timeout value of the router in cycles
        """
        return _decode_router_timeout_value(self._router_emergency_timeout)

    @property
    def n_dropped_packets(self):
        """ The number of packets dropped by the router and received by\
            the reinjector (may not fit in the queue though)
        """
        return self._n_dropped_packets

    @property
    def n_missed_dropped_packets(self):
        """ The number of times that when a dropped packet was read it was\
            found that another one or more packets had also been dropped,\
            but had been missed
        """
        return self._n_missed_dropped_packets

    @property
    def n_dropped_packet_overflows(self):
        """ Of the n_dropped_packets received, how many were lost due to not\
            having enough space in the queue of packets to reinject
        """
        return self._n_dropped_packet_overflows

    @property
    def n_processor_dumps(self):
        """ The number of times that when a dropped packet was caused due to
        a processor failing to take the packet.

        :return: int
        """
        return self._n_processor_dumps

    @property
    def n_link_dumps(self):
        """ The number of times that when a dropped packet was caused due to
        a link failing to take the packet.

        :return: int
        """
        return self._n_link_dumps

    @property
    def n_reinjected_packets(self):
        """ Of the n_dropped_packets received, how many packets were\
            successfully reinjected
        """
        return self._n_reinjected_packets

    @property
    def is_reinjecting_multicast(self):
        """ True if reinjection of multicast packets is enabled
        """
        return self._flags & DPRIFlags.MULTICAST.value != 0

    @property
    def is_reinjecting_point_to_point(self):
        """ True if reinjection of point-to-point packets is enabled
        """
        return self._flags & DPRIFlags.POINT_TO_POINT.value != 0

    @property
    def is_reinjecting_nearest_neighbour(self):
        """ True if reinjection of nearest neighbour packets is enabled
        """
        return (self._flags &
                DPRIFlags.NEAREST_NEIGHBOUR.value != 0)

    @property
    def is_reinjecting_fixed_route(self):
        """ True if reinjection of fixed-route packets is enabled
        """
        return self._flags & DPRIFlags.FIXED_ROUTE.value != 0
