from spinnman.transceiver import create_transceiver_from_hostname
import time

machine = "spinn-10.cs.man.ac.uk"
# machine = "192.168.240.253"

transceiver = create_transceiver_from_hostname(machine)
size_in_mbs = 10.0
start = float(time.time())
result = transceiver.read_memory(0, 0, 0x70000000, int(size_in_mbs * 1024 * 1024))
for array in result:
    pass
end = float(time.time())
seconds = float(end - start)
speed = (size_in_mbs * 8) / seconds

print ("Read {} MB in {} seconds ({} Mb/s)".format(size_in_mbs, seconds, speed))
