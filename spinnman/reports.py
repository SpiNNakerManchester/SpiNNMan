import os
import time
import logging

logger = logging.getLogger(__name__)


def generate_machine_report(report_directory, machine, connections):
    """
    Generate report on the physical structure of the target SpiNNaker machine.
    """
    file_name = report_directory + os.sep + "machine_structure.rpt"
    f_machine_struct = None
    try:
        f_machine_struct = open(file_name, "w")
    except IOError:
        logger.error("Generate_placement_reports: Can't open file {} for "
                     "writing.".format(file_name))
    f_machine_struct.write("        Target SpiNNaker Machine Structure\n")
    f_machine_struct.write("        ==================================\n\n")
    time_date_string = time.strftime("%c")
    f_machine_struct.write("Generated: %s" % time_date_string)
    f_machine_struct.write(" for target machine '{}'".format(connections))
    f_machine_struct.write("\n\n")

    x_dim = machine.max_chip_x + 1
    y_dim = machine.max_chip_y + 1
    f_machine_struct.write("Machine dimensions (in chips) x : {}  y : {}\n\n"
                           .format(x_dim, y_dim))

    # TODO: Add further details on the target machine.

    # Close file:
    f_machine_struct.close()