import os
import time
import logging

logger = logging.getLogger(__name__)


def generate_machine_report(report_directory, machine, connections):
    """Generate report on the physical structure of the target SpiNNaker \
    machine.

    :param report_directory: the directory to which reports are stored
    :param machine: the machine python object
    :param connections: the list of connections to the machine
    :type report_directory: str
    :type machine: spinnmachine.machine.Machine object
    :type connections: iterable of implementations of \
        spinnman.connections.abstract_classes.connection.AbstractConnection
    :rtype: None
    :raise IOError: when a file cannot be opened for some reason
    """
    file_name = report_directory + os.sep + "machine_structure.rpt"
    time_date_string = time.strftime("%c")
    try:
        with open(file_name, "w") as f:
            f.write("\t\tTarget SpiNNaker Machine Structure\n")
            f.write("\t\t==================================\n\n")
            f.write("Generated: %s" % time_date_string)
            f.write(" for target machine '{}'".format(connections))
            f.write("\n\n")

            x_dim = machine.max_chip_x + 1
            y_dim = machine.max_chip_y + 1
            f.write("Machine dimensions (in chips) x : {}  y : {}\n\n".format(
                x_dim, y_dim))

            # TODO: Add further details on the target machine.
            f.write("\t\tMachine router information\n")
            f.write("\t\t==========================\n\n")
            for x in range(machine.max_chip_x + 1):
                for y in range(machine.max_chip_y + 1):
                    chip = machine.get_chip_at(x, y)
                    if chip:
                        f.write("Information for chip {}:{}\n".format(
                            chip.x, chip.y))
                        f.write("Neighbouring chips \n{}\n".format(
                            chip.router.get_neighbouring_chips_coords()))
                        f.write("Router list of links for this chip are: \n")
                        for link in chip.router.links:
                            f.write("\t{}\n".format(link))
                        f.write("\t\t==========================\n\n")
    except IOError:
        logger.error("Generate_placement_reports: Can't open file {} for "
                     "writing.".format(file_name))
        raise
