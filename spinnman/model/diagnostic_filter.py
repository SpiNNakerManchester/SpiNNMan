from spinnman.model.enums import \
    DiagnosticFilterDestination, DiagnosticFilterSource, \
    DiagnosticFilterPayloadStatus, DiagnosticFilterDefaultRoutingStatus, \
    DiagnosticFilterEmergencyRoutingStatus, DiagnosticFilterPacketType

# Bit offsets of the various fields in the filter word
_PACKET_TYPE_OFFSET = 0
_EMERGENCY_ROUTE_OFFSET = 4
_EMERGENCY_ROUTE_MODE_OFFSET = 8
_DEFAULT_ROUTE_OFFSET = 10
_PAYLOAD_OFFSET = 12
_SOURCE_OFFSET = 14
_DESTINATION_OFFSET = 16
_ENABLE_INTERRUPT_OFFSET = 30


# Uses an enum to set flags in the filter word from a given offset
def _set_flags_in_word(word, enum_list, enum_type, offset):
    if enum_list is None:
        enum_values = list()
    else:
        enum_values = list(enum_list)
    if len(enum_values) == 0:
        enum_values = [value for value in enum_type]
    for enum_value in enum_values:
        word |= 1 << (enum_value.value + offset)
    return word


# Uses an enum to read flags in the filter word from a given offset
def _read_flags_from_word(word, enum_list, offset):
    flags = list()
    for enum_value in enum_list:
        if word & 1 << (enum_value.value + offset) != 0:
            flags.append(enum_value)
    return flags


class DiagnosticFilter(object):
    """ A router diagnostic counter filter, which counts packets passing
        through the router with certain properties.  The counter will be\
        incremented so long as the packet matches one of the values in each\
        field i.e. one of each of the destinations, sources, payload_statuses,\
        default_routing_statuses, emergency_routing_statuses and packet_types
    """

    def __init__(self, enable_interrupt_on_counter_event,
                 match_emergency_routing_status_to_incoming_packet,
                 destinations, sources, payload_statuses,
                 default_routing_statuses, emergency_routing_statuses,
                 packet_types):
        """
        :param enable_interrupt_on_counter_event: Indicates whether\
                    an interrupt should be raised when this rule matches
        :type enable_interrupt_on_counter_event: bool
        :param match_emergency_routing_status_to_incoming_packet: Indicates\
                    whether the emergency routing statuses should be matched\
                    against packets arriving at this router (if True), or if\
                    they should be matched against packets leaving this router\
                    (if False)
        :type match_emergency_routing_status_to_incoming_packet: bool
        :param destinations: Increment the counter if one or more of the given\
                    destinations match
        :type destinations: iterable of\
                    :py:class:`spinnman.model.diagnostic_filter_destination.DiagnosticFilterDestination`

        :param sources: Increment the counter if one or more of the given\
                    sources match (or None or empty list to match all)
        :type sources: iterable of\
                    :py:class:`spinnman.model.diagnostic_filter_source.DiagnosticFilterSource`
        :param payload_statuses: Increment the counter if one or more of the\
                    given payload statuses match  (or None or empty list to \
                    match all)
        :type payload_statuses: iterable of\
                    :py:class:`spinnman.model.diagnostic_filter_payload_status.DiagnosticFilterPayloadStatus`
        :param default_routing_statuses: Increment the counter if one or more\
                    of the given default routing statuses match  (or None or \
                    empty list to match all)
        :type default_routing_statuses: iterable of\
                    :py:class:`spinnman.model.diagnostic_filter_default_routing_status.DiagnosticFilterDefaultRoutingStatus`
        :param emergency_routing_statuses: Increment the counter if one or\
                    more of the given emergency routing statuses match  (or \
                    None or empty list to match all)
        :type emergency_routing_statuses: iterable of\
                    :py:class:`spinnman.model.diagnostic_filter_emergency_routing_status.DiagnosticFilterEmergencyRoutingStatus`
        :param packet_types: Increment the counter if one or more\
                    of the given packet types match  (or None or empty list to\
                    match all)
        :type packet_types: iterable of\
                    :py:class:`spinnman.model.diagnostic_filter_packet_type.DiagnosticFilterPacketType`
        """

        self._enable_interrupt_on_counter_event = \
            enable_interrupt_on_counter_event
        self._match_emergency_routing_status_to_incoming_packet = \
            match_emergency_routing_status_to_incoming_packet
        self._destinations = destinations
        self._sources = sources
        self._payload_statuses = payload_statuses
        self._default_routing_statuses = default_routing_statuses
        self._emergency_routing_statuses = emergency_routing_statuses
        self._packet_types = packet_types

    @property
    def enable_interrupt_on_counter_event(self):
        return self._enable_interrupt_on_counter_event

    @property
    def match_emergency_routing_status_to_incoming_packet(self):
        return self._match_emergency_routing_status_to_incoming_packet

    @property
    def destinations(self):
        return self._destinations

    @property
    def sources(self):
        return self._sources

    @property
    def payload_statuses(self):
        return self._payload_statuses

    @property
    def default_routing_statuses(self):
        return self._default_routing_statuses

    @property
    def emergency_routing_statuses(self):
        return self._emergency_routing_statuses

    @property
    def packet_types(self):
        return self._packet_types

    @property
    def filter_word(self):
        """ A word of data that can be written to the router to set up\
            the filter
        """
        data = 0
        if self._enable_interrupt_on_counter_event:
            data |= 1 << _ENABLE_INTERRUPT_OFFSET
        if not self._match_emergency_routing_status_to_incoming_packet:
            data |= 1 << _EMERGENCY_ROUTE_MODE_OFFSET
        data = _set_flags_in_word(data, self._destinations,
                                  DiagnosticFilterDestination,
                                  _DESTINATION_OFFSET)
        data = _set_flags_in_word(data, self._sources,
                                  DiagnosticFilterSource,
                                  _SOURCE_OFFSET)
        data = _set_flags_in_word(data, self._payload_statuses,
                                  DiagnosticFilterPayloadStatus,
                                  _PAYLOAD_OFFSET)
        data = _set_flags_in_word(data, self._default_routing_statuses,
                                  DiagnosticFilterDefaultRoutingStatus,
                                  _DEFAULT_ROUTE_OFFSET)
        data = _set_flags_in_word(data, self._emergency_routing_statuses,
                                  DiagnosticFilterEmergencyRoutingStatus,
                                  _EMERGENCY_ROUTE_OFFSET)
        data = _set_flags_in_word(data, self._packet_types,
                                  DiagnosticFilterPacketType,
                                  _PACKET_TYPE_OFFSET)

        return data

    @staticmethod
    def read_from_int(int_value):
        enable_interrupt_on_counter_event = (
            (int_value >> _ENABLE_INTERRUPT_OFFSET) & 0x1) == 1
        match_emergency_routing_status_to_incoming_packet = (
            (int_value >> _EMERGENCY_ROUTE_MODE_OFFSET) & 0x1) == 0
        destinations = _read_flags_from_word(
            int_value, DiagnosticFilterDestination, _DESTINATION_OFFSET)
        sources = _read_flags_from_word(
            int_value, DiagnosticFilterSource, _SOURCE_OFFSET)
        payload_statuses = _read_flags_from_word(
            int_value, DiagnosticFilterPayloadStatus, _PAYLOAD_OFFSET)
        default_routing_statuses = _read_flags_from_word(
            int_value, DiagnosticFilterDefaultRoutingStatus,
            _DEFAULT_ROUTE_OFFSET)
        emergency_routing_statuses = _read_flags_from_word(
            int_value, DiagnosticFilterEmergencyRoutingStatus,
            _EMERGENCY_ROUTE_OFFSET)
        packet_types = _read_flags_from_word(
            int_value, DiagnosticFilterPacketType, _PACKET_TYPE_OFFSET)

        return DiagnosticFilter(
            enable_interrupt_on_counter_event,
            match_emergency_routing_status_to_incoming_packet,
            destinations, sources, payload_statuses, default_routing_statuses,
            emergency_routing_statuses, packet_types)
