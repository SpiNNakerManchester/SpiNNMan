__author__ = 'stokesa6'
from spinnman.interfaces.load_interfaces.\
    abstract_load_data_interface import AbstractLoadDataInterface

class LoadDataInterfaceFromFile(AbstractLoadDataInterface):
    """class used to read load data from a file object"""

    def __init__(self, file_names_data):
        """constructor method for initilising a load data interface from file

        :param file_names_data: the lsit of filenames and x,y,p,mem_bases
        :type file_names_data: iterable of tuples
        :return: a LoadDataInterfaceFromFile object
        :rtype: spinnman.interfaces.load_interfaces.\
                load_data_interface_from_file.LoadDataInterfaceFromFile
        :raise: IOError
        """
        AbstractLoadDataInterface.__init__(self)
        self.data_points = file_names_data

    def get_data_for_core(self, x, y, p, base_address, chunk_size):
        """a helper method that returns a iterable object of chunks of a data\
           object needed to be loaded in the board

        :param x: chip id in x dimension
        :param y: chip id in y dimension
        :param p: chip cpu id
        :param base_address: the start address in memory that this data is \
                             being written
        :param chunk_size: the size of each chunk
        :type x: int
        :type y: int
        :type p: int
        :type base_address: 0x
        :type chunk_size: int
        :return: an iterable object fo chunks
        :rtype: iterable object
        :raise: IOError
        """
        pass

    def contains_cores(self):
        """a helper method that returns the list of cores and mem addresses \
           stored in this object

        :return: list of tuples each containing x,y,p,mem_base
        :rtype: iterble of tuples
        :raise: IOError
        """
        pass

    def get_no_blocks(self, x, y, p, base_address, chunk_size):
        """a helper method that returns the number of iterable chunks for a \
           given cores data to be written at the base address

        :param x: chip id in x dimension
        :param y: chip id in y dimension
        :param p: chip cpu id
        :param base_address: the start address in memory that this data is \
                             being written
        :param chunk_size: the size of each chunk
        :type x: int
        :type y: int
        :type p: int
        :type base_address: 0x
        :type chunk_size: int
        :return: the number of iterable chunks
        :rtype: int
        :raise: IOError
        """
        pass
