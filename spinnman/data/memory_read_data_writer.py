from spinnman.data.abstract_read_data_writer import AbstractReadDataWriter

class MemoryReadDataWriter(AbstractReadDataWriter):
    """ A memory-based implementation of AbstractReadDataWriter
    """
    
    def __init__(self):
        """
        """
        pass
    
    def write_bytes(self, data, offset=0, length=None):
        """ See :py:meth:`spinnman.data.abstract_read_data_writer.AbstractReadDataWriter.write_bytes`
        """
        pass
    
    def close(self):
        """ See :py:meth:`spinnman.data.abstract_read_data_writer.AbstractReadDataWriter.close`
        """
        pass
    
    def get_bytes(self):
        """ Get the bytes stored in this writer
        
        :return: The bytes stored
        :rtype: bytearray
        :raise None: No known exceptions are raised
        """
        pass
