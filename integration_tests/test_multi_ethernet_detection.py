from spalloc.job import Job

from spinnman.exceptions import SpinnmanGenericProcessException
from spinnman.transceiver import create_transceiver_from_hostname
import logging


logging.basicConfig(level=logging.INFO)

print "Getting board"
job = Job(3, hostname="192.168.2.100", owner="Me!!!!")
job.wait_until_ready()
try:
    transceiver = create_transceiver_from_hostname(job.hostname, 5)

    print "Booting"
    transceiver.ensure_board_is_ready()

    try:
        transceiver.discover_scamp_connections()
    except SpinnmanGenericProcessException as e:
        print "bollocks"
        transceiver._update_machine()

    transceiver._update_machine()

    print "Reading connections"
    connections = transceiver._scamp_connections
    if len(connections) != 3:
        raise Exception("did not detect correct number of ethernet, "
                        "detected {} connections".format(len(connections)))
    transceiver.close()
finally:
    print "Closing"
    job.destroy()