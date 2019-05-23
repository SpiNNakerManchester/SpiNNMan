import os.path
import time
import logging
from spinn_utilities.log import FormatAdapter

logger = FormatAdapter(logging.getLogger(__name__))


def generate_machine_report(report_directory, machine, connections):
    """ Generate report on the physical structure of the target SpiNNaker \
        machine.

    :param report_directory: the directory to which reports are stored
    :param machine: the machine python object
    :param connections: the list of connections to the machine
    :type report_directory: str
    :type machine: :py:class:`spinn_machine.Machine`
    :type connections: \
        iterable(:py:class:`spinnman.connections.abstract_classes.AbstractConnection`)
    :rtype: None
    :raise IOError: when a file cannot be opened for some reason
    """
    file_name = os.path.join(report_directory, "machine_structure.rpt")
    time_date_string = time.strftime("%c")
    try:
        with open(file_name, "w") as f:
            _write_header(f, time_date_string, machine, connections)
            # TODO: Add further details on the target machine.
            for chip in machine.chips:
                _write_chip_router_report(f, chip)
    except IOError:
        logger.exception(
            "Generate_placement_reports: Can't open file {} for writing.",
            file_name)
        raise


def _write_header(f, timestamp, machine, connections):
    f.write("\t\tTarget SpiNNaker Machine Structure\n")
    f.write("\t\t==================================\n")
    f.write("\nGenerated: {} for target machine '{}'\n\n".format(
        timestamp, connections))
    f.write("Machine dimensions (in chips) x : {}  y : {}\n\n".format(
        machine.max_chip_x + 1, machine.max_chip_y + 1))
    f.write("\t\tMachine router information\n")
    f.write("\t\t==========================\n")


def _write_chip_router_report(f, chip):
    f.write("\nInformation for chip {}:{}\n".format(chip.x, chip.y))
    f.write("Neighbouring chips \n{}\n".format(
        chip.router.get_neighbouring_chips_coords()))
    f.write("Router list of links for this chip are: \n")
    for link in chip.router.links:
        f.write("\t{}\n".format(link))
    f.write("\t\t==========================\n")
