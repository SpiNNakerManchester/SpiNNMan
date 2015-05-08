import socket
import struct
import select
import time

machine = "spinn-10.cs.man.ac.uk"
mbs = 10.0

start = float(time.time())
remote_ip_address = socket.gethostbyname(machine)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((remote_ip_address, 17893))
sock.settimeout(1.0)

n_bytes = mbs * 1024.0 * 1024.0

in_progress = 0
offset = 0x70000000
sequence = 0
while n_bytes > 0:

    bytes_to_get = n_bytes
    if bytes_to_get > 256:
        bytes_to_get = 256

    request = struct.pack("<2x8B", 0x87, 0xFF,
                          ((0x0 & 0x7) << 5) | (0x0 & 0x1F),
                          ((0x7 & 0x7) << 5) | (31 & 0x1F), 0, 0, 0, 0)
    request += struct.pack("<2H", 2, sequence)
    request += struct.pack("<I", offset)
    request += struct.pack("<I", bytes_to_get)
    request += struct.pack("<I", 0)
    sequence = sequence + 1 % 65536
    sock.send(request)
    in_progress += 1

    if in_progress >= 1:

        while in_progress > 1:
            raw_data = sock.recv(512)
            in_progress -= 1

    n_bytes -= bytes_to_get
    offset += bytes_to_get

end = float(time.time())
seconds = float(end - start)
speed = (mbs * 8) / seconds

print ("Read {} MB in {} seconds ({} Mb/s)".format(mbs, seconds, speed))
