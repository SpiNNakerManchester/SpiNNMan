__author__ = 'stokesa6'


class _MachineCalls(object):
    """machine specific commands are stored here for clarity"""

    def __init__(self, transciever):
        """place holder for any machineCall specific constuctions

        :param transciever: the parent object which contains other calls
        :type transciever: spinnman.interfaces.transceiver.Transciever
        :return: a new MachineCalls object
        :rtype: spinnman.interfaces.transceiver_tools.\
                machine_calls._MachineCalls
        :raise: None: does not raise any known exceptions

        """
        self.transciever = transciever


    def reset_board(self):
        """ allows the trnasciever to reset the board if applicable

        :return: None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        pass

    def check_target_machine(self, hostname, x, y):
        """This routine takes the requested dimension hints and the hostname of\
           the machine, then checks that it is pingable on the network, has \
           been booted and has physical dimensions that at least match the \
           requested dimensions.

        :param hostname:   address of the physical machine that we'll be using
        :param x:          dimensions requested of the machine (may be smaller\
                           than the physical machine, but not bigger!)
        :param y:          dimensions requested of the machine (may be smaller\
                           than the physical machine, but not bigger!)
        :type hostname: int
        :type x: int
        :type y: int
        :return: xdims,ydims, list of chips with spec that were detected in \
                  the machine
        :rtype: tuple
        :raise spinnman.exceptions.ExploreException: when an error occurs \
                                                       during the exploration \
                                                       of the machine

        """

    def _list_avilable_machine_spec(self, hostname, x, y):
        """explores the board and returns a list of tuples for each chip in the\
           machine

        :param hostname:   address of the physical machine that we'll be using
        :param x:          dimensions requested of the machine (may be smaller\
                           than the physical machine, but not bigger!)
        :param y:          dimensions requested of the machine (may be smaller\
                           than the physical machine, but not bigger!)
        :type hostname: int
        :type x: int
        :type y: int
        :return: list of chips with spec that were detected in \
                  the machine
        :rtype: iterable object of tuple
        :raise spinnman.exceptions.ExploreException: when an error occurs \
                                                       during the exploration \
                                                       of the machine
        """
        pass

    def explore_a_reboot(self, hostname):
        """checks to see if a reboot can happen and reboots the board if\
           possible

        :param hostname: the machine name of the board
        :return: None
        :rtype: None
        :raise None: does not raise any known exceptions
        """
        pass

    def boot(self, hostname):
        """supports booting the board from the transciever

        :param hostname: the machine name of the board
        :return: None
        :rtype: None
        :raise None: does not raise any known exceptions
        """
        pass


