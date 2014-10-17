from spinnman.transceiver import create_transceiver_from_hostname

import logging
from spinnman.model.cpu_state import CPUState
from spinnman.model.core_subsets import CoreSubsets
from spinnman.model.core_subset import CoreSubset
from random import randint
from spinnman.data.file_data_reader import FileDataReader
from os.path import os
from time import sleep
from spinnman.messages.scp.scp_signal import SCPSignal
from spinnman.model.iptag.iptag import IPTag
from spinn_machine.multicast_routing_entry import MulticastRoutingEntry
import sys
from spinnman.model.iptag.reverse_iptag import ReverseIPTag
logging.basicConfig(level=logging.INFO)
logging.getLogger("spinnman.transceiver").setLevel(logging.DEBUG)

machine = "spinn-10.cs.man.ac.uk"
version = 2

#machine = "spinn-1.cs.man.ac.uk"
#version = 5

#machine = "192.168.240.253"
#version = 3

n_cores = 20
core_subsets = CoreSubsets(core_subsets=[CoreSubset(0, 0, range(1, 11)),
                                         CoreSubset(1, 1, range(1, 11))])
app_id = 30

down_cores = CoreSubsets()
down_cores.add_processor(0, 0, 5)
down_chips = CoreSubsets(core_subsets=[CoreSubset(0, 1, [])])
transceiver = create_transceiver_from_hostname(machine, False, ignore_cores=down_cores, ignore_chips=down_chips)

try:
    print "Version Information"
    print "==================="
    version_info = transceiver.ensure_board_is_ready(version)
    print version_info
    print ""

    print "Clear Router Diagnostics"
    print "========================"
    transceiver.clear_router_diagnostics(0, 0)
    router_diagnostics = transceiver.get_router_diagnostics(0, 0)
    print router_diagnostics.registers
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
    read_data_packets = transceiver.read_memory(0, 0, 0x70000000, 1000)
    read_data = bytearray()
    for packet in read_data_packets:
        read_data.extend(packet)
    print "Written:", map(hex, write_data)
    print "Read:   ", map(hex, read_data)
    print ""

    print "Flood Memory Write"
    print "=================="
    transceiver.write_memory_flood(0x70000000, 0x04050607)
    read_data_packets = transceiver.read_memory(1, 1, 0x70000000, 4)
    for packet in read_data_packets:
        print map(hex, packet)
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

    print "Send SYNC0"
    print "=========="
    transceiver.send_signal(app_id, SCPSignal.SYNC0)
    count = 0
    while count < 20:
        count = transceiver.get_core_state_count(app_id, CPUState.FINSHED)
        print "Cores in state FINISHED={}".format(count)
        sleep(0.1)
    print ""

    print "Get IOBufs"
    print "=========="
    iobufs = transceiver.get_iobuf(core_subsets)
    iobufs = sorted(iobufs, key=lambda x: (x.x, x.y, x.p))
    for iobuf in iobufs:
        print iobuf
    print ""

    print "Stop Application"
    print "================"
    transceiver.send_signal(app_id, SCPSignal.STOP)
    cpu_infos = transceiver.get_cpu_information(core_subsets)
    cpu_infos = sorted(cpu_infos, key=lambda x: (x.x, x.y, x.p))
    print "{} CPUs".format(len(cpu_infos))
    for cpu_info in cpu_infos:
        print cpu_info
    print ""

    print "Create IP Tags"
    print "=============="
    transceiver.set_ip_tag(IPTag(".", 50000, 1))
    transceiver.set_ip_tag(IPTag(".", 60000, 2, strip_sdp=True))
    transceiver.set_reverse_ip_tag(ReverseIPTag(40000, 3, 0, 1, 2))
    tags = transceiver.get_ip_tags()
    for tag in tags:
        print tag
    print ""

    print "Clear IP Tag"
    print "============"
    transceiver.clear_ip_tag(1)
    transceiver.clear_ip_tag(2)
    transceiver.clear_ip_tag(3)
    tags = transceiver.get_ip_tags()
    for tag in tags:
        print tag
    print ""

    print "Load Routes"
    print "==========="
    routes = [MulticastRoutingEntry(0x10000000, 0xFFFF7000,
            (1, 2, 3, 4, 5), (0, 1, 2), False)]
    transceiver.load_multicast_routes(0, 0, routes, app_id)
    routes = transceiver.get_multicast_routes(0, 0, app_id)
    for route in routes:
        print "Key={}, Mask={}, processors={}, links={}".format(
                hex(route.key), hex(route.mask), route.processor_ids,
                route.link_ids)
    print ""

    print "Clear Routes"
    print "============"
    transceiver.clear_multicast_routes(0, 0)
    routes = transceiver.get_multicast_routes(0, 0)
    for route in routes:
        print "Key={}, Mask={}, processors={}, links={}".format(
                hex(route.key), hex(route.mask), route.processor_ids,
                route.link_ids)
    print ""

    print "Get Router Diagnostics"
    print "======================"
    router_diagnostics = transceiver.get_router_diagnostics(0, 0)
    print router_diagnostics.registers
    print ""

except Exception:
    logging.exception("Error!")

transceiver.close()
