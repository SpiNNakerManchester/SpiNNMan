__author__ = 'stokesa6'
class MemoryCalls(object):
    """memory specific commands are stored here for clarity"""

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
        self.transceiver = transceiver

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

    def write_mem_from_file(self, start_addr, type, filename, chunk_size=16384):
        """Uploads the contents of a file to the target SpiNNaker node at a \
           specific memory location.

        :param start_addr: base address for the uploaded data
        :param type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD`` \
                     to indicate element type
        :param filename: name of the source file to read from
        :param chunk_size: number of bytes to read from the file in one go
        :type start_addr: int
        :type type: int
        :type filename: str
        :type chunk_size: int
        :return: the current file position
        :rtype: int
        :raises: IOError, SCPError
        """
        pass

    def read_mem(self, start_addr, scamp_type, size):
        """Reads an amount of data from the target SpiNNaker node starting at
           address ``start_addr``.

        :param start_addr: address to start reading from
        :param scamp_type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD`` \
                     to indicate element type
        :param size: number of bytes to read
        :type start_addr: int
        :type scamp_type: int
        :type size: int
        :returns: the data read
        :rtype: str
        :raises: spinnMan.spinnman_exceptions.SCPError
        """
        pass

    def read_mem_to_file(self, start_addr, type, size, filename,
                         chunk_size=16384):
        """Reads the memory of a target SpiNNaker node, starting from a \
           specific location, and then writes it into a file.

        :param start_addr: address to start reading from
        :param type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD`` to \
                     indicate element type
        :param filename:   name of the destination file to write into
        :param chunk_size: number of bytes to write to the file in one go
        :type start_addr: int
        :type type: int
        :type filename: str
        :type chunk_size: int
        :raises: IOError, SCPError
        """
        pass

