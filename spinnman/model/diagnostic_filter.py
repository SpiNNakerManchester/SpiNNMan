# Copyright (c) 2015 The University of Manchester
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
from __future__ import annotations
from enum import Enum
from typing import List, Type, TypeVar
from spinnman.model.enums import (
    DiagnosticFilterDestination, DiagnosticFilterSource,
    DiagnosticFilterPayloadStatus, DiagnosticFilterDefaultRoutingStatus,
    DiagnosticFilterEmergencyRoutingStatus, DiagnosticFilterPacketType)
#: :meta private:
E = TypeVar("E", bound=Enum)

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
def _set_flags_in_word(
        word: int, enum_list: List[E], enum_type: Type[E],
        offset: int) -> int:
    if enum_list is None:
        enum_values: List[E] = list()
    else:
        enum_values = list(enum_list)
    if not enum_values:
        enum_values = [value for value in enum_type]
    for enum_value in enum_values:
        word |= 1 << (enum_value.value + offset)
    return word


# Uses an enum to read flags in the filter word from a given offset
def _read_flags_from_word(
        word: int, enum_list: Type[E], offset: int) -> List[E]:
    flags: List[E] = list()
    for enum_value in enum_list:
        if word & 1 << (enum_value.value + offset) != 0:
            flags.append(enum_value)
    return flags


class DiagnosticFilter(object):
    """
    A router diagnostic counter filter, which counts packets passing
    through the router with certain properties.  The counter will be
    incremented so long as the packet matches one of the values in each
    field i.e. one of each of the destinations, sources, payload_statuses,
    default_routing_statuses, emergency_routing_statuses and packet_types.
    """
    __slots__ = [
        "_default_routing_statuses",
        "_destinations",
        "_emergency_routing_statuses",
        "_enable_interrupt_on_counter_event",
        "_match_emergency_routing_status_to_incoming_packet",
        "_packet_types",
        "_payload_statuses",
        "_sources"]

    def __init__(self, enable_interrupt_on_counter_event: bool,
                 match_emergency_routing_status_to_incoming_packet: bool,
                 destinations: List[DiagnosticFilterDestination],
                 sources: List[DiagnosticFilterSource],
                 payload_statuses: List[DiagnosticFilterPayloadStatus],
                 default_routing_statuses: List[
                     DiagnosticFilterDefaultRoutingStatus],
                 emergency_routing_statuses: List[
                     DiagnosticFilterEmergencyRoutingStatus],
                 packet_types: List[DiagnosticFilterPacketType]):
        """
        :param enable_interrupt_on_counter_event: Indicates whether
            an interrupt should be raised when this rule matches
        :param match_emergency_routing_status_to_incoming_packet:
            Indicates whether the emergency routing statuses should be matched
            against packets arriving at this router (if True), or if they
            should be matched against packets leaving this router (if False)
        :param destinations:
            Increment the counter if one or more of the given destinations
            match
        :param sources:
            Increment the counter if one or more of the given sources match
            (or `None` or empty list to match all)
        :param payload_statuses:
            Increment the counter if one or more of the given payload statuses
            match (or `None` or empty list to match all)
        :param default_routing_statuses:
            Increment the counter if one or more of the given default routing
            statuses match (or `None` or empty list to match all)
        :param emergency_routing_statuses:
            Increment the counter if one or more of the given emergency routing
            statuses match (or `None` or empty list to match all)
        :param packet_types:
            Increment the counter if one or more of the given packet types
            match (or `None` or empty list to match all)
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
    def enable_interrupt_on_counter_event(self) -> bool:
        """
        Returns the enable interrupt on counter event passed into
        the init unchanged

        Currently unused
        """
        return self._enable_interrupt_on_counter_event

    @property
    def match_emergency_routing_status_to_incoming_packet(self) -> bool:
        """
        Returns the match emergency routing status to incoming packet passed
        into the init unchanged

        Currently unused
        """
        return self._match_emergency_routing_status_to_incoming_packet

    @property
    def destinations(self) -> List[DiagnosticFilterDestination]:
        """
        Returns the destinations passed into the init unchanged

        Currently unused
        """
        return self._destinations

    @property
    def sources(self) -> List[DiagnosticFilterSource]:
        """
        Returns the sources passed into the init unchanged

        Currently unused
        """
        return self._sources

    @property
    def payload_statuses(self) -> List[DiagnosticFilterPayloadStatus]:
        """
        Returns the payload statuses passed into the init unchanged

        Currently unused
        """
        return self._payload_statuses

    @property
    def default_routing_statuses(self) -> List[
            DiagnosticFilterDefaultRoutingStatus]:
        """
        Returns the default routing statuses passed into the init unchanged

        Currently unused
        """
        return self._default_routing_statuses

    @property
    def emergency_routing_statuses(self) -> List[
            DiagnosticFilterEmergencyRoutingStatus]:
        """
        Returns the emergency routing statuses passed into the init unchanged

        Currently unused
        """
        return self._emergency_routing_statuses

    @property
    def packet_types(self) -> List[DiagnosticFilterPacketType]:
        """
        Returns the packet types passed into the init unchanged

        Currently unused
        """
        return self._packet_types

    @property
    def filter_word(self) -> int:
        """
        A word of data that can be written to the router to set up the filter.
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
    def read_from_int(int_value: int) -> DiagnosticFilter:
        """
        Claims to return a filter that reads an int

        Currently only called by unused Transceiver methods

        :param int_value:
        :returns: Untested filter
        """
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
