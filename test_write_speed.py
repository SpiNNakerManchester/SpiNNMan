from spinnman.transceiver import create_transceiver_from_hostname
import time
import numpy

machine = "spinn-10.cs.man.ac.uk"
# machine = "192.168.240.253"

transceiver = create_transceiver_from_hostname(machine)
size_in_mbs = 10.0
size_in_bytes = size_in_mbs * 1000 * 1000
data = bytearray(numpy.random.randint(0, 256, size_in_bytes))
start = float(time.time())
transceiver.write_memory(1, 0, 0x70000000, data, size_in_bytes)
end = float(time.time())
seconds = float(end - start)
speed = (size_in_mbs * 8) / seconds

print ("Wrote {} MB in {} seconds ({} Mb/s)".format(size_in_mbs, seconds, speed))
