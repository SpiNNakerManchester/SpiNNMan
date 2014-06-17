__author__ = 'stokesa6'
class PacketCalls(object):
    """packet specific commands are stored here for clarity"""

    def __init__(self, transceiver):
        """the memory_calls object is used to contain calls which are specific\
           to reading / writing and accessing memory. These can be:\
           \
           reading memory (file or ram)\
           writing memory (file or ram)\
           slice a container into smaller chunks\
           :param transceiver: the parent object which contains other calls
           :type transceiver: spinnman.interfaces.transceiver.Transciever
           :return: a new memoryCalls object
           :rtype: spinnman.interfaces.transceiver_tools.memory_calls.MemoryCalls
           :raise: None: does not raise any known exceptions
        """
        self.nn_id = 0


    def set_view(self, new_x, new_y, new_cpu, new_node):
        """ updates the chip and processor that is currently under focus

            :param new_x: the new x value of the chip to move focus to
            :param new_y: the new y value of the chip to move focus to
            :param new_cpu: the new p value of the chip to move focus to
            :param new_node: the new x|y|p value to move focus to
            :type new_x: int
            :type new_y: int
            :type new_cpu:int
            :type new_node:int
            :return: None
            :rtype: None
            :raise: None: does not raise any known exceptions
        """
        pass

    def flood_fill(self, buf, region, mask, app_id, app_flags, base=0x67800000):
        """executes a flood fill of a buffer to all cores in a region that \
           respond to a given application id.

           :param buf: the data to flood fill down to a given set of chips/cores
           :param region: defines which chips/cores are to be flood filled
           :param mask: used to determine which cores are flood filled.
           :param app_id: which application this flood fill comes from
           :param app_flags: what behaviour is to occur after the flood fill
           :param base: the base location in SDRAM to start writing
           :type buf:
           :type region: int
           :type mask:int
           :type app_id:int
           :type app_flags: int
           :type base: hex value
           :return: None
           :rtype: None
           :raise: spinnman.spinnman_exceptions.SCPError
        """
        pass

    def nnp(self, key, data, sfr):
        """
        :param key: entry for arg1 of a scp message
        :param data: the data inside a scp message
        :param sfr: entry for arg3 of a scp message
        :type key: int
        :type data: str
        :type sfr: int
        :return None
        :rtype: None
        :raise: spinnman.spinnman_exceptions.SCPError
        """
        pass

    def next_id(self):
        """
        :return None
        :rtype: None
        :raise: None: does not raise any known exceptions
        """
        pass
