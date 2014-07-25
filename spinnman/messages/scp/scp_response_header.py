from spinnman.exceptions import SpinnmanIOException
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.exceptions import SpinnmanInvalidPacketException
from spinnman.messages.scp.scp_result import SCPResult


class SCPResponseHeader(object):
    """ Represents the header of an SCP Response
    """
    
    def __init__(self):
        """
        """
        self._result = None
        self._sequence = None
        
    @property
    def result(self):
        """ The result of the SCP response
        
        :return: The result
        :rtype: :py:class:`spinnman.messages.scp.scp_result.SCPResult`
        """
        return self._result
    
    @property
    def sequence(self):
        """ The sequence number of the SCP response
        
        :return: The sequence number of the packet, between 0 and 65535
        :rtype: int
        """
        return self._sequence
        
    def read_scp_response_header(self, byte_reader):
        """ Read an SCP header from a byte_reader
        
        :param byte_reader: The reader to read the data from
        :type byte_reader:\
                    :py:class:`spinnman.data.abstract_byte_reader.AbstractByteReader`
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanIOException: If there is an error\
                    reading from the reader
        :raise spinnman.exceptions.SpinnmanInvalidPacketException: If there\
                    are not enough bytes to read the header
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is an error setting any of the values
        """
        result_value = None
        try:
            result_value = byte_reader.read_short()
            self._result = SCPResult(result_value)
            self._sequence = byte_reader.read_short()
        except ValueError:
            raise SpinnmanInvalidParameterException(
                "result", result_value,
                "Unrecognized result")
        except IOError as exception:
            raise SpinnmanIOException(str(exception))
        except EOFError:
            raise SpinnmanInvalidPacketException(
                "SCP (header)",
                "Not enough data to read the header")
