__author__ = 'stokesa6'
class MemoryCalls(object):

    def __init__(self, transceiver):
        """ the memory_calls object is used to contain calls which are specific\
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

    def write_mem(self, start_addr, type, data):
        """Uploads data to a target SpiNNaker node at a specific memory \
           location.

        :param start_addr: base address for the uploaded data
        :param type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD``\
                     to indicate element type
        :param data: string of data to upload
        :type start_addr: int
        :type type: int
        :type data: str
        :return: None
        :rtype: None
        :raise: spinnman.spinnman_exceptions.SCPError
        """

    def gen_slice(self, seq, length):
        """Generator function to slice a container into smaller chunks.

        :param seq: a container to store chunks
        :param length: length of each slice of ``seq``
        :type seq: iterable container
        :type length: int
        :return: appropriate slice of ``seq``
        :rtype: iterable container
        :raise StopIteration
        """
        pass

    def _check_size_alignment(self, scamp_type, size):
        """Utility function to ensure that ``size`` is of the correct alignment\
           for the data-type in ``type``.

        :param scamp_type: one of the ``TYPE_BYTE``, ``TYPE_HALF``, or
                          ``TYPE_WORD`` constants
        :param size: size (in bytes) of the data
        :type scamp_type: int
        :type size: int
        :return: None
        :rtype: None
        :raise: ValueError

        """