__author__ = 'stokesa6'

class Machine_calls(object):
    """machine specific commands are stored here for clarity"""

    def __init__(self, transciever):
        """

        """
        self.transciever = transciever


    def reset_board(self):
        pass

    def check_target_machine(self, hostname, x, y):
        """
        This routine takes the requested dimension hints and the hostname of the machine,
            then checks that it is pingable on the network, has been booted and has physical
            dimensions that at least match the requested dimensions.

        :param int hostname:   address of the physical machine that we'll be using
        :param int x:          dimensions requested of the machine (may be smaller than the physical machine, but not bigger!)
        :param int y:          dimensions requested of the machine (may be smaller than the physical machine, but not bigger!)
        :returns:              xdims, and ydims which contain the physical dimensions detected in the machine
        :raises:               ExploreException

        """

    def explore_a_reboot(self, hostname):
        pass

    def boot(self, hostname):
        pass


