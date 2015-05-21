import time
from spinnman.messages.scp.scp_result import SCPResult
from spinnman.exceptions import SpinnmanTimeoutException
from spinnman.connections.udp_packet_connections.udp_spinnaker_connection \
    import UDPSpinnakerConnection
from spinnman.messages.scp.impl.scp_read_memory_request \
    import SCPReadMemoryRequest

# machine = "spinn-10.cs.man.ac.uk"
machine = "192.168.240.253"
mbs = 10.0

start = float(time.time())
connections = [UDPSpinnakerConnection(remote_host=machine) for _ in range(1)]
requests = dict()
times_sent = dict()

n_bytes = mbs * 1000.0 * 1000.0
chip_x = 0
chip_y = 0
cpu = 0

in_progress = 0
offset = 0x70000000
sequence = 0
total_bytes = 0
retry_codes = set([SCPResult.RC_TIMEOUT,
                   SCPResult.RC_P2P_TIMEOUT,
                   SCPResult.RC_LEN])


def do_retrieve(connection, in_progress, n_packets):
    global total_bytes
    to_resend = list()
    while in_progress > n_packets:
        try:
            result, seq, raw_data = connection.receive_scp_response()
            if seq in requests:
                request_sent = requests.pop(seq)
                times_sent.pop(seq)
                if result in retry_codes:
                    to_resend.append((seq, request_sent))
                else:
                    response = request_sent.get_scp_response()
                    response.read_bytestring(raw_data)
                    total_bytes += len(response._data)
                in_progress -= 1
        except SpinnmanTimeoutException:
            pass

        now = time.time()
        for seq, time_sent in times_sent.iteritems():
            if now - time_sent >= 1.0:
                to_resend.append((seq, requests[seq]))
                in_progress -= 1

    for seq, request_to_resend in to_resend:
        connection.send_scp_request(request_to_resend)
        times_sent[seq] = time.time()
        in_progress += 1
    return in_progress

next_connection = 0
while n_bytes > 0:

    bytes_to_get = min((n_bytes, 256))

    request = SCPReadMemoryRequest(0, 0, offset, bytes_to_get)
    request.scp_request_header.sequence = sequence
    requests[sequence] = request
    times_sent[sequence] = time.time()
    sequence = (sequence + 1) % 65536
    connection = connections[next_connection]
    next_connection = (next_connection + 1) % len(connections)
    connection.send_scp_request(request)
    in_progress += 1

    if in_progress >= 16:
        in_progress = do_retrieve(connection, in_progress, 8)

    n_bytes -= bytes_to_get
    offset += bytes_to_get

do_retrieve(connection, in_progress, 0)

end = float(time.time())
seconds = float(end - start)
speed = (mbs * 8) / seconds

print ("Read {} MB in {} seconds ({} Mb/s)".format(mbs, seconds, speed))
print total_bytes
