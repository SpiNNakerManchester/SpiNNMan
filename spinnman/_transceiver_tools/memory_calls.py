__author__ = 'stokesa6'


class _MemoryCalls(object):
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
            :rtype: spinnman.interfaces.transceiver_tools.memory_calls\
                    ._MemoryCalls
            :raise: None: does not raise any known exceptions
        """
        self.transceiver = transceiver

    def write_mem(self, start_addr, scamp_type, data, chip_x, chip_y, chip_cpu):
        """Uploads data to a target SpiNNaker node at a specific memory \
           location.

        :param start_addr: base address for the uploaded data
        :param scamp_type: one of ``TYPE_BYTE``, ``TYPE_HALF``, \
                           or ``TYPE_WORD`` to indicate element type
        :param data: string of data to upload
        :param chip_x: id of a chip in the x dimension
        :param chip_y: id of a chip in the y dimension
        :param chip_cpu: id of a processor on a given chip defined by chip_x, \
                         chip_y
        :type start_addr: int
        :type scamp_type: int
        :type data: str
        :type chip_x: int
        :type chip_y: int
        :type chip_cpu: int
        :return: None
        :rtype: None
        :raise spinnman.exceptions.SpinnmanSCPError:\
               whens an error occurs at the connection level
        """

    def _gen_slice(self, seq, length):
        """Generator function to slice a container into smaller chunks.

        :param seq: a container to store chunks
        :param length: length of each slice of ``seq``
        :type seq: iterable container
        :type length: int
        :return: appropriate slice of ``seq``
        :rtype: iterable container
        :raise StopIteration: when asked to return a slice from a competed \
                              iteration
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
        :raise ValueError: when the size is not word alligned
        """

    def write_mem_from_file(self, start_addr, scamp_type, filename, chip_x,
                            chip_y, chip_cpu, chunk_size=16384):
        """Uploads the contents of a file to the target SpiNNaker node at a \
           specific memory location.

        :param start_addr: base address for the uploaded data
        :param scamp_type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD`` \
                     to indicate element type
        :param filename: name of the source file to read from
        :param chunk_size: number of bytes to read from the file in one go
        :param chip_x: id of a chip in the x dimension
        :param chip_y: id of a chip in the y dimension
        :param chip_cpu: id of a processor on a given chip defined by chip_x, \
                         chip_y
        :type start_addr: int
        :type scamp_type: int
        :type filename: str
        :type chunk_size: int
        :type chip_x: int
        :type chip_y: int
        :type chip_cpu: int
        :return: the current file position
        :rtype: int
        :raise IOError: when something goes wrong with reading a file
        :raise spinnman.exceptions.SpinnmanSCPError: \
               whens an error occurs at the connection level
        """
        pass

    def read_mem(self, start_addr, scamp_type, size, chip_x, chip_y, chip_cpu):
        """Reads an amount of data from the target SpiNNaker node starting at
           address ``start_addr``.

        :param start_addr: address to start reading from
        :param scamp_type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD`` \
                     to indicate element type
        :param size: number of bytes to read
        :param chip_x: id of a chip in the x dimension
        :param chip_y: id of a chip in the y dimension
        :param chip_cpu: id of a processor on a given chip defined by chip_x, \
                         chip_y
        :type start_addr: int
        :type scamp_type: int
        :type size: int
        :type chip_x: int
        :type chip_y: int
        :type chip_cpu: int
        :return: the data read
        :rtype: str
        :raise spinnman.exceptions.SpinnmanSCPError: \
                      whens an error occurs at the connection level
        """
        pass

    def read_mem_to_file(self, start_addr, scamp_type, size, filename, chip_x, 
                         chip_y, chip_cpu, chunk_size=16384):
        """Reads the memory of a target SpiNNaker node, starting from a \
           specific location, and then writes it into a file.

        :param start_addr: address to start reading from
        :param type: one of ``TYPE_BYTE``, ``TYPE_HALF``, or ``TYPE_WORD`` to \
                     indicate element type
        :param filename:   name of the destination file to write into
        :param chunk_size: number of bytes to write to the file in one go
        :param chip_x: id of a chip in the x dimension
        :param chip_y: id of a chip in the y dimension
        :param chip_cpu: id of a processor on a given chip defined by chip_x, \
                         chip_y
        :type start_addr: int
        :type type: int
        :type filename: str
        :type chunk_size: int
        :type chip_x: int
        :type chip_y: int
        :type chip_cpu: int
        :return: None
        :rtype: None
        :raise IOError: something goes wrong with writing to a file
        :raise spinnman.exceptions.SpinnmanSCPError:\
                      whens an error occurs at the connection level
        """
        pass

