import logging

from spinnman.transceiver import create_transceiver_from_hostname
from spinnman.model.core_subsets import CoreSubsets
from spinnman.model.core_subset import CoreSubset

logging.basicConfig(level=logging.INFO)

machine = "spinn-1.cs.man.ac.uk"
version = 2

#machine = "spinn-1.cs.man.ac.uk"
#version = 5

#machine = "192.168.240.253"
#version = 3

n_cores = 20
core_subsets = CoreSubsets(core_subsets=[CoreSubset(0, 0, range(1, 11))])
app_id = 30

transceiver = create_transceiver_from_hostname(machine, False)

print "CPU Information"
print "==============="
cpu_infos = transceiver.get_cpu_information(core_subsets)
cpu_infos = sorted(cpu_infos, key=lambda x: (x.x, x.y, x.p))
print "{} CPUs".format(len(cpu_infos))
for cpu_info in cpu_infos:
    print cpu_info
print ""