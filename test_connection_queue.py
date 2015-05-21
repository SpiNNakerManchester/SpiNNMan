from spinnman.connections.udp_packet_connections.udp_spinnaker_connection import UDPSpinnakerConnection
from spinnman.messages.scp.impl.scp_read_memory_request import SCPReadMemoryRequest
from spinnman.connections.scp_request_set import SCPRequestSet

import time
import traceback
import sys

machine = "spinn-10.cs.man.ac.uk"
# machine = "192.168.240.253"
mbs = 10.0

connection = UDPSpinnakerConnection(remote_host=machine)
queue = SCPRequestSet(connection)

n_bytes = mbs * 1000.0 * 1000.0

start = float(time.time())
in_progress = 0
offset = 0x70000000
sequence = 0
total_bytes = 0


def handle_exception(request, exception, traceback_list):
    print exception
    for line in traceback.format_list(traceback_list):
        print line
    sys.exit()


def handle_response(response):
    global total_bytes
    total_bytes += len(response.data)

while n_bytes > 0:

    bytes_to_get = n_bytes
    if bytes_to_get > 256:
        bytes_to_get = 256

    queue.send_request(SCPReadMemoryRequest(0, 0, offset, bytes_to_get),
                       handle_response,
                       handle_exception)

    n_bytes -= bytes_to_get
    offset += bytes_to_get
queue.finish()

end = float(time.time())
seconds = float(end - start)
speed = (mbs * 8) / seconds

print ("Read {} MB in {} seconds ({} Mb/s)".format(mbs, seconds, speed))
print queue.n_timeouts, "timeouts"
print queue.n_channels, "channels"
print queue.n_resent, "resent"
print total_bytes
