import logging
from random import randint
from os.path import os

from spinnman.transceiver import create_transceiver_from_hostname
from spinnman.model.cpu_state import CPUState
from spinnman.model.core_subsets import CoreSubsets
from spinnman.model.core_subset import CoreSubset
from spinnman.data.file_data_reader import FileDataReader
from time import sleep
from spinnman.messages.scp.scp_signal import SCPSignal
from spinn_machine.tags.iptag import IPTag
from spinn_machine.multicast_routing_entry import MulticastRoutingEntry
from spinn_machine.tags.reverse_iptag import ReverseIPTag
from spinnman.model.diagnostic_filter import DiagnosticFilter
import struct
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest
from spinnman.model.diagnostic_filter_destination \
    import DiagnosticFilterDestination
from spinnman.model.diagnostic_filter_packet_type \
    import DiagnosticFilterPacketType
from board_test_configuration import BoardTestConfiguration

logging.basicConfig(level=logging.INFO)
logging.getLogger("spinnman.transceiver").setLevel(logging.DEBUG)


board_config = BoardTestConfiguration()
board_config.set_up_remote_board()

n_cores = 20
core_subsets = CoreSubsets(core_subsets=[CoreSubset(0, 0, range(1, 11)),
                                         CoreSubset(1, 1, range(1, 11))])
app_id = 30

down_cores = CoreSubsets()
down_cores.add_processor(0, 0, 5)
down_chips = CoreSubsets(core_subsets=[CoreSubset(0, 1, [])])


def print_enums(name, enum_list):
    string = ""
    for enum_value in enum_list:
        string += enum_value.name + "; "
    print name, string


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
    print prefix, values
    values = ""
    for i in reversed(range(start, end)):
        if i in start_fields:
            values += "|"
        values += str(i % 10)
        if i in end_fields:
            values += "|"
    print prefix, values
    for i in reversed(range(start, end)):
        if i in start_fields:
            prefix += "|"
        prefix += "="
        if i in end_fields:
            prefix += "|"
    print "", prefix
    string = ""
    for i in reversed(range(start, end)):
        if i in start_fields:
            string += "|"
        string += str((word >> i) & 0x1)
        if i in end_fields:
            string += "|"
    print name, string


def print_filter(d_filter):
    print_word_as_binary(
        "Filter word:", d_filter.filter_word,
        fields=[(31, 31), (30, 30), (29, 29), (28, 25), (24, 16), (15, 14),
                (13, 12), (11, 10), (9, 9), (8, 8), (7, 4), (3, 0)])
    print "Enable Interrupt:", d_filter.enable_interrupt_on_counter_event
    print "Emergency Routing Status on Incoming:",\
        d_filter.match_emergency_routing_status_to_incoming_packet
    print_enums("Destinations:", d_filter.destinations)
    print_enums("Sources:", d_filter.sources)
    print_enums("Payloads:", d_filter.payload_statuses)
    print_enums("Default Routing:", d_filter.default_routing_statuses)
    print_enums("Emergency Routing:", d_filter.emergency_routing_statuses)
    print_enums("Packet Types:", d_filter.packet_types)

transceiver = create_transceiver_from_hostname(
    board_config.remotehost, ignore_cores=down_cores, ignore_chips=down_chips)


try:
    print "Version Information"
    print "==================="
    version_info = transceiver.ensure_board_is_ready(
        board_config.board_version)
    print version_info
    print ""

    print "Discovering other connections to the machine"
    print "==================="
    connections = transceiver.discover_scamp_connections()
    print connections
    print ""

    print "Machine Details"
    print "==============="
    machine = transceiver.get_machine_details()
    print machine
    print ""

    print "Memory Write and Read"
    print "====================="
    write_data = bytearray(randint(0, 255) for i in range(0, 1000))
    transceiver.write_memory(0, 0, 0x70000000, write_data)
    read_data = transceiver.read_memory(0, 0, 0x70000000, 1000)
    print "Written:", map(hex, write_data)
    print "Read:   ", map(hex, read_data)
    print ""

    print "Flood Memory Write"
    print "=================="
    transceiver.write_memory_flood(0x70000000, 0x04050607)
    read_data = transceiver.read_memory(1, 1, 0x70000000, 4)
    print hex(struct.unpack("<I", read_data)[0])
    print ""

    print "Execute Flood"
    print "============="
    file_size = os.stat("hello.aplx").st_size
    executable = FileDataReader("hello.aplx")
    transceiver.execute_flood(core_subsets, executable, app_id, file_size)
    count = 0
    while count < 20:
        count = transceiver.get_core_state_count(app_id, CPUState.SYNC0)
        print "Cores in state SYNC0={}".format(count)
        sleep(0.1)
    print ""

    print "CPU Information"
    print "==============="
    cpu_infos = transceiver.get_cpu_information(core_subsets)
    cpu_infos = sorted(cpu_infos, key=lambda x: (x.x, x.y, x.p))
    print "{} CPUs".format(len(cpu_infos))
    for cpu_info in cpu_infos:
        print cpu_info
    print ""

#     print "Send SYNC0"
#     print "=========="
#     transceiver.send_signal(app_id, SCPSignal.SYNC0)
#     count = 0
#     while count < 20:
#         count = transceiver.get_core_state_count(app_id, CPUState.FINSHED)
#         print "Cores in state FINISHED={}".format(count)
#         sleep(0.1)
#     print ""
#
#     print "Get IOBufs"
#     print "=========="
#     iobufs = transceiver.get_iobuf(core_subsets)
#     iobufs = sorted(iobufs, key=lambda x: (x.x, x.y, x.p))
#     for iobuf in iobufs:
#         print iobuf
#     print ""
#
#     print "Stop Application"
#     print "================"
#     transceiver.send_signal(app_id, SCPSignal.STOP)
#     cpu_infos = transceiver.get_cpu_information(core_subsets)
#     cpu_infos = sorted(cpu_infos, key=lambda x: (x.x, x.y, x.p))
#     print "{} CPUs".format(len(cpu_infos))
#     for cpu_info in cpu_infos:
#         print cpu_info
#     print ""
#
#     print "Create IP Tags"
#     print "=============="
#     transceiver.set_ip_tag(IPTag(None, 1, ".", 50000))
#     transceiver.set_ip_tag(IPTag(None, 2, ".", 60000, strip_sdp=True))
#     transceiver.set_reverse_ip_tag(ReverseIPTag(None, 3, 40000, 0, 1, 2))
#     tags = transceiver.get_tags()
#     for tag in tags:
#         print tag
#     print ""
#
#     print "Clear IP Tag"
#     print "============"
#     transceiver.clear_ip_tag(1)
#     transceiver.clear_ip_tag(2)
#     transceiver.clear_ip_tag(3)
#     tags = transceiver.get_tags()
#     for tag in tags:
#         print tag
#     print ""
#
#     print "Load Routes"
#     print "==========="
#     routes = [MulticastRoutingEntry(0x10000000, 0xFFFF7000,
#               (1, 2, 3, 4, 5), (0, 1, 2), False)]
#     transceiver.load_multicast_routes(0, 0, routes, app_id)
#     routes = transceiver.get_multicast_routes(0, 0, app_id)
#     for route in routes:
#         print "Key={}, Mask={}, processors={}, links={}".format(
#             hex(route.key_combo), hex(route.mask), route.processor_ids,
#             route.link_ids)
#     print ""
#
#     print "Clear Routes"
#     print "============"
#     transceiver.clear_multicast_routes(0, 0)
#     routes = transceiver.get_multicast_routes(0, 0)
#     for route in routes:
#         print "Key={}, Mask={}, processors={}, links={}".format(
#             hex(route.key_combo), hex(route.mask), route.processor_ids,
#             route.link_ids)
#     print ""
#
#     print "Set Router Diagnostic Filter"
#     print "============================="
#     destinations = [DiagnosticFilterDestination.LINK_0,
#                     DiagnosticFilterDestination.LINK_1,
#                     DiagnosticFilterDestination.LINK_2,
#                     DiagnosticFilterDestination.LINK_5]
#     for i in range(len(destinations)):
#         current_filter = DiagnosticFilter(
#             enable_interrupt_on_counter_event=False,
#             match_emergency_routing_status_to_incoming_packet=True,
#             destinations=[destinations[i]], sources=None,
#             payload_statuses=None, default_routing_statuses=[],
#             emergency_routing_statuses=[],
#             packet_types=[DiagnosticFilterPacketType.POINT_TO_POINT])
#         transceiver.set_router_diagnostic_filter(0, 0, i + 12, current_filter)
#
#     print "Clear Router Diagnostics"
#     print "========================"
#     transceiver.clear_router_diagnostic_counters(0, 0)
#     router_diagnostics = transceiver.get_router_diagnostics(0, 0)
#     print router_diagnostics.registers
#     print ""
#
#     print "Send read requests"
#     print "======================"
#     transceiver.send_scp_message(SCPReadMemoryRequest(1, 0, 0x70000000, 4))
#     transceiver.send_scp_message(SCPReadMemoryRequest(1, 1, 0x70000000, 4))
#     transceiver.send_scp_message(SCPReadMemoryRequest(1, 1, 0x70000000, 4))
#     transceiver.send_scp_message(SCPReadMemoryRequest(0, 1, 0x70000000, 4))
#     transceiver.send_scp_message(SCPReadMemoryRequest(0, 1, 0x70000000, 4))
#     transceiver.send_scp_message(SCPReadMemoryRequest(0, 1, 0x70000000, 4))
#
#     print "Get Router Diagnostics"
#     print "======================"
#     router_diagnostics = transceiver.get_router_diagnostics(0, 0)
#     print router_diagnostics.registers
#     print ""
#
#     print "Get Router Diagnostic Filters"
#     print "============================="
#     for i in range(0, 16):
#         print "Filter", i, ":"
#         current_filter = transceiver.get_router_diagnostic_filter(0, 0, i)
#         print_filter(current_filter)
#         print ""

except Exception:
    logging.exception("Error!")

transceiver.close()
