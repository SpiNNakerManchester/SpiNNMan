# Copyright (c) 2014 The University of Manchester
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

"""
To run this you need an hello.aplx

to build that cd into this directory
then run

make -f $SPINN_DIRS/make/app.make APP=hello

"""
import logging
from random import randint
import struct
import time
from spinn_machine import CoreSubsets, CoreSubset, MulticastRoutingEntry
from spinn_machine.tags import IPTag, ReverseIPTag
from spinnman.data import SpiNNManDataView
from spinnman.config_setup import unittest_setup
from spinnman.transceiver import create_transceiver_from_hostname
from spinnman.model.enums import CPUState
from spinnman.messages.scp.enums import Signal
from spinnman.model import DiagnosticFilter
from spinnman.messages.scp.impl import ReadMemory
from spinnman.model.enums import (
    DiagnosticFilterDestination, DiagnosticFilterPacketType)
from spinnman.constants import ROUTER_REGISTER_REGISTERS
from spinnman.board_test_configuration import BoardTestConfiguration

logging.basicConfig(level=logging.INFO)
logging.getLogger("spinnman.transceiver").setLevel(logging.DEBUG)

board_config = BoardTestConfiguration()
board_config.set_up_remote_board()

n_cores = 20
core_subsets = CoreSubsets(core_subsets=[CoreSubset(0, 0, range(1, 11)),
                                         CoreSubset(1, 1, range(1, 11))])


def print_enums(name, enum_list):
    string = ""
    for enum_value in enum_list:
        string += enum_value.name + "; "
    print(name, string)


def print_word_as_binary(name, word, start=0, end=32, fields=None):
    start_fields = set()
    end_fields = set()
    if fields is not None:
        for field in fields:
            start_fields.add(field[0])
        for field in fields:
            if (field[1] - 1) not in start_fields:
                end_fields.add(field[1])

    prefix = ""
    for i in range(len(name)):
        prefix += " "
    values = ""
    for i in reversed(range(start, end)):
        if i in start_fields:
            values += "|"
        if i % 10 == 0:
            values += str(i / 10)
        else:
            values += " "
        if i in end_fields:
            values += "|"
    print(prefix, values)
    values = ""
    for i in reversed(range(start, end)):
        if i in start_fields:
            values += "|"
        values += str(i % 10)
        if i in end_fields:
            values += "|"
    print(prefix, values)
    for i in reversed(range(start, end)):
        if i in start_fields:
            prefix += "|"
        prefix += "="
        if i in end_fields:
            prefix += "|"
    print("", prefix)
    string = ""
    for i in reversed(range(start, end)):
        if i in start_fields:
            string += "|"
        string += str((word >> i) & 0x1)
        if i in end_fields:
            string += "|"
    print(name, string)


def print_filter(d_filter):
    print_word_as_binary(
        "Filter word:", d_filter.filter_word,
        fields=[(31, 31), (30, 30), (29, 29), (28, 25), (24, 16), (15, 14),
                (13, 12), (11, 10), (9, 9), (8, 8), (7, 4), (3, 0)])
    print("Enable Interrupt:", d_filter.enable_interrupt_on_counter_event)
    print("Emergency Routing Status on Incoming:",
          d_filter.match_emergency_routing_status_to_incoming_packet)
    print_enums("Destinations:", d_filter.destinations)
    print_enums("Sources:", d_filter.sources)
    print_enums("Payloads:", d_filter.payload_statuses)
    print_enums("Default Routing:", d_filter.default_routing_statuses)
    print_enums("Emergency Routing:", d_filter.emergency_routing_statuses)
    print_enums("Packet Types:", d_filter.packet_types)


def print_reinjection_status(status):
    print("Dropped Packets captured:", status.n_dropped_packets)
    print("Missed drop packets:", status.n_missed_dropped_packets)
    print("Dropped Packet overflows:", status.n_dropped_packet_overflows)
    print("Reinjected packets:", status.n_reinjected_packets)
    print("Router timeout: {}  emergency timeout {}".format(
        status.router_timeout, status.router_emergency_timeout))
    print(("Re-injecting multicast: {}  point_to_point: {}  nearest_neighbour:"
           " {}  fixed_route: {}").format(
               status.is_reinjecting_multicast,
               status.is_reinjecting_point_to_point,
               status.is_reinjecting_nearest_neighbour,
               status.is_reinjecting_fixed_route))


class Section(object):
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        print(self.msg)
        print("=" * len(self.msg))

    def __exit__(self, *_ignored):
        print("")
        return False


def print_transceiver_tests(transceiver):

    with Section("Version Information"):
        version_info = transceiver.ensure_board_is_ready()
        print(version_info)

    app_id = SpiNNManDataView().get_new_id()

    with Section("Discovering other connections to the machine"):
        connections = transceiver.discover_scamp_connections()
        print(connections)

    with Section("Machine Details"):
        machine = transceiver.get_machine_details()
        print(machine)
        print(machine.boot_chip)

    with Section("Memory Write and Read"):
        write_data = bytearray(randint(0, 255) for i in range(0, 1000))
        transceiver.write_memory(0, 0, 0x70000000, write_data)
        read_data = transceiver.read_memory(0, 0, 0x70000000, 1000)
        print("Written:", map(hex, write_data))
        print("Read:   ", map(hex, read_data))

    with Section("Flood Memory Write"):
        transceiver.write_memory_flood(0x70000000, 0x04050607)
        read_data = transceiver.read_memory(1, 1, 0x70000000, 4)
        print(hex(struct.unpack("<I", read_data)[0]))

    with Section("Execute Flood"):
        transceiver.execute_flood(
            core_subsets, "hello.aplx", app_id, is_filename=True)
        count = 0
        while count < 20:
            count = transceiver.get_core_state_count(app_id, CPUState.SYNC0)
            print("Cores in state SYNC0={}".format(count))
            time.sleep(0.1)

    with Section("CPU Information"):
        cpu_infos = transceiver.get_cpu_infos(core_subsets)
        cpu_infos = sorted(cpu_infos, key=lambda x: (x.x, x.y, x.p))
        print("{} CPUs".format(len(cpu_infos)))
        for cpu_info in cpu_infos:
            print(cpu_info)

    with Section("Send SYNC0"):
        transceiver.send_signal(app_id, Signal.SYNC0)
        count = 0
        while count < 20:
            count = transceiver.get_core_state_count(app_id, CPUState.FINISHED)
            print("Cores in state FINISHED={}".format(count))
            time.sleep(0.1)

    with Section("Get IOBufs"):
        iobufs = transceiver.get_iobuf(core_subsets)
        for iobuf in iobufs:
            print(iobuf)

    with Section("Stop Application"):
        transceiver.send_signal(app_id, Signal.STOP)
        time.sleep(0.5)
        cpu_infos = transceiver.get_cpu_infos(core_subsets)
        cpu_infos = sorted(cpu_infos, key=lambda x: (x.x, x.y, x.p))
        print("{} CPUs".format(len(cpu_infos)))
        for cpu_info in cpu_infos:
            print(cpu_info)

    with Section("Create IP Tags"):
        transceiver.set_ip_tag(IPTag(None, 0, 0, 1, ".", 50000))
        transceiver.set_ip_tag(
            IPTag(None, 0, 0, 2, ".", 60000, strip_sdp=True))
        transceiver.set_reverse_ip_tag(ReverseIPTag(None, 3, 40000, 0, 1, 2))
        tags = transceiver.get_tags()
        for tag in tags:
            print(tag)

    with Section("Clear IP Tag"):
        transceiver.clear_ip_tag(1)
        transceiver.clear_ip_tag(2)
        transceiver.clear_ip_tag(3)
        tags = transceiver.get_tags()
        for tag in tags:
            print(tag)

    with Section("Load Routes"):
        routes = [MulticastRoutingEntry(0x10000000, 0xFFFF7000,
                  processor_ids=(1, 2, 3, 4, 5), link_ids=(0, 1, 2),
                  defaultable=False)]
        transceiver.load_multicast_routes(0, 0, routes, app_id)
        routes = transceiver.get_multicast_routes(0, 0, app_id)
        for route in routes:
            print("Key={}, Mask={}, processors={}, links={}".format(
                hex(route.routing_entry_key), hex(route.mask),
                route.processor_ids, route.link_ids))

    with Section("Clear Routes"):
        transceiver.clear_multicast_routes(0, 0)
        routes = transceiver.get_multicast_routes(0, 0)
        for route in routes:
            print("Key={}, Mask={}, processors={}, links={}".format(
                hex(route.routing_entry_key), hex(route.mask),
                route.processor_ids, route.link_ids))

    with Section("Set Router Diagnostic Filter"):
        destinations = [DiagnosticFilterDestination.LINK_0,
                        DiagnosticFilterDestination.LINK_1,
                        DiagnosticFilterDestination.LINK_2,
                        DiagnosticFilterDestination.LINK_5]
        for i in range(len(destinations)):
            current_filter = DiagnosticFilter(
                enable_interrupt_on_counter_event=False,
                match_emergency_routing_status_to_incoming_packet=True,
                destinations=[destinations[i]], sources=None,
                payload_statuses=None, default_routing_statuses=[],
                emergency_routing_statuses=[],
                packet_types=[DiagnosticFilterPacketType.POINT_TO_POINT])
            transceiver.set_router_diagnostic_filter(
                0, 0, i + 12, current_filter)

    with Section("Clear Router Diagnostics"):
        transceiver.clear_router_diagnostic_counters(
            0, 0, counter_ids=[ROUTER_REGISTER_REGISTERS.LOC_PP.value,
                               ROUTER_REGISTER_REGISTERS.EXT_PP.value])
        diagnostics = transceiver.get_router_diagnostics(0, 0)
        for register in ROUTER_REGISTER_REGISTERS:
            print("{}: {}".format(
                register.name, diagnostics.registers[register.value]))

    with Section("Send read requests"):
        transceiver.send_scp_message(ReadMemory(1, 0, 0x70000000, 4))
        transceiver.send_scp_message(ReadMemory(1, 1, 0x70000000, 4))
        transceiver.send_scp_message(ReadMemory(1, 1, 0x70000000, 4))
        transceiver.send_scp_message(ReadMemory(0, 1, 0x70000000, 4))
        transceiver.send_scp_message(ReadMemory(0, 1, 0x70000000, 4))
        transceiver.send_scp_message(ReadMemory(0, 1, 0x70000000, 4))

    with Section("Get Router Diagnostics"):
        diagnostics = transceiver.get_router_diagnostics(0, 0)
        for register in ROUTER_REGISTER_REGISTERS:
            print("{}: {}".format(
                register.name, diagnostics.registers[register.value]))

    with Section("Get Router Diagnostic Filters"):
        for i in range(0, 16):
            print("Filter", i, ":")
            current_filter = transceiver.get_router_diagnostic_filter(0, 0, i)
            print_filter(current_filter)
            print("")

    # 8-byte numbers have to be converted into bytearrays to be written
    inputdata = struct.pack("<Q", 123456789123456789)

    with Section("Test writing bytearrays and ints to write memory and "
                 "extracting them"):
        transceiver.write_memory(0, 0, 0x70000000, data=inputdata)
        data = struct.unpack(
            "<Q", transceiver.read_memory(0, 0, 0x70000000, 8))[0]
        if data != 123456789123456789:
            raise ValueError("values are not identical")
        transceiver.write_memory(0, 0, 0x70000000, data=int(123456789))
        data = struct.unpack(
            "<I", transceiver.read_memory(0, 0, 0x70000000, 4))[0]
        if data != 123456789:
            raise ValueError("values are not identical")

    with Section("Test writing bytearrays and ints to write_neighbour_memory "
                 "and extracting them"):
        transceiver.write_neighbour_memory(0, 0, 0, 0x70000000, inputdata)
        data = struct.unpack(
            "<Q", transceiver.read_neighbour_memory(0, 0, 0, 0x70000000, 8))[0]
        if data != 123456789123456789:
            raise ValueError("values are not identical")

        transceiver.write_neighbour_memory(0, 0, 0, 0x70000000, 123456789)
        data = struct.unpack(
            "<I", transceiver.read_neighbour_memory(0, 0, 0, 0x70000000, 4))[0]
        if data != 123456789:
            raise ValueError("values are not identical")

    with Section("Test writing bytearrays and ints to write_memory_flood and "
                 "extracting them"):
        transceiver.write_memory_flood(0x70000000, data=inputdata)
        data = struct.unpack(
            "<Q", transceiver.read_memory(0, 0, 0x70000000, 8))[0]
        data2 = struct.unpack(
            "<Q", transceiver.read_memory(1, 1, 0x70000000, 8))[0]
        if data != 123456789123456789 or data2 != 123456789123456789:
            raise ValueError("values are not identical")

        transceiver.write_memory_flood(0x70000000, data=123456789)
        data = struct.unpack(
            "<I", transceiver.read_memory(0, 0, 0x70000000, 4))[0]
        data2 = struct.unpack(
            "<I", transceiver.read_memory(1, 1, 0x70000000, 4))[0]
        if data != 123456789 or data2 != 123456789:
            raise ValueError("values are not identical")

    with Section("Get Heap"):
        for heap_element in transceiver.get_heap(0, 0):
            print(heap_element)


unittest_setup()
with create_transceiver_from_hostname(
        board_config.remotehost, board_config.board_version,
        bmp_connection_data=board_config.bmp_names,
        auto_detect_bmp=board_config.auto_detect_bmp) as _transceiver:
    print_transceiver_tests(_transceiver)
