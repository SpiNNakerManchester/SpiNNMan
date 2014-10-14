import os
import time
import logging

logger = logging.getLogger(__name__)


def generate_machine_report(report_directory, machine, connections):
    """Generate report on the physical structure of the target SpiNNaker \
    machine.

    :param report_directory: the directroy to which reports are stored
    :param machine: the machine python object
    :param connections: the list of connections to the machine
    :type report_directory: str
    :type machine: spinnmachine.machine.Machine object
    :type connections: iterable of implientations of
    spinnman.connections.abstract_connection.AbstractConnection
    :return None
    :rtype: None
    :raise IOError: when a file cannot be opened for some reason
    """
    file_name = report_directory + os.sep + "machine_structure.rpt"
    f_machine_struct = None
    try:
        f_machine_struct = open(file_name, "w")
    except IOError:
        logger.error("Generate_placement_reports: Can't open file {} for "
                     "writing.".format(file_name))
    f_machine_struct.write("\t\tTarget SpiNNaker Machine Structure\n")
    f_machine_struct.write("\t\t==================================\n\n")
    time_date_string = time.strftime("%c")
    f_machine_struct.write("Generated: %s" % time_date_string)
    f_machine_struct.write(" for target machine '{}'".format(connections))
    f_machine_struct.write("\n\n")

    x_dim = machine.max_chip_x + 1
    y_dim = machine.max_chip_y + 1
    f_machine_struct.write("Machine dimensions (in chips) x : {}  y : {}\n\n"
                           .format(x_dim, y_dim))

    # TODO: Add further details on the target machine.
    f_machine_struct.write("\t\tMachine router information\n")
    f_machine_struct.write("\t\t==========================\n\n")
    chips = machine.chips
    for x in range(machine.max_chip_x + 1):
        for y in range(machine.max_chip_y + 1):
            chip = machine.get_chip_at(x, y)
            if chip:
                f_machine_struct.write("Information for chip {}:{}\n"
                                       .format(chip.x, chip.y))
                f_machine_struct.write(
                    "Neighbouring chips \n{}\n"
                    .format(chip.router.get_neighbouring_chips_coords()))
                f_machine_struct.write("Router list of links for this chip"
                                       " are: \n")
                for link in chip.router.links:
                    f_machine_struct.write("\t{}\n".format(link))
                f_machine_struct.write("\t\t==========================\n\n")
    # Close file:
    f_machine_struct.close()


