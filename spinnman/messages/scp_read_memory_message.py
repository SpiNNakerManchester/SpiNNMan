from spinnman.messages.scp_message import SCPMessage
from spinnman.exceptions import SpinnmanInvalidParameterException
from spinnman.messages.sdp_flag import SDPFlag
from spinnman.messages.scp_command import SCPCommand
   

class SCPReadMemoryMessage(SCPMessage):
    """ An SCP message for reading a region of memory
    """
    
    def __init__(self, x, y, base_address, size):
        """ 
        
        
        :param x: The x-coordinate of the chip to read from, between 0 and 255
        :type x: int
        :param y: The y-coordinate of the chip to read from, between 0 and 255
        :type y: int
        :param base_address: The positive base address to start the read from
        :type base_address: int
        :param size: The number of bytes to read, between 1 and 256
        :type size: int
        :param sequence: The optional sequence number of the packet, between\
                    0 and 65535
        :type sequence: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException:
                    * If the chip coordinates are out of range
                    * If the base address is not a positive number
                    * If the size is out of range
                    * If the tag is out of range
                    * If the sequence number if not a positive number
        """
        if base_address < 0:
            raise SpinnmanInvalidParameterException(
                    "base_address", str(base_address),
                    "Must be a positive number")
        
        if size < 1 or size > 256:
            raise SpinnmanInvalidParameterException(
                    "size", size, "Must be between 1 and 256")
        
        super(SCPReadMemoryMessage, self).__init__(
                flags=SDPFlag.REPLY_EXPECTED, destination_port=1, 
                destination_chip_x=x, destination_chip_y=y, destination_cpu=0, 
                command=SCPCommand.CMD_READ, argument_1=base_address, 
                argument_2=size, argument_3=0)
