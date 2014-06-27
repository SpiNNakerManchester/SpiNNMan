from enum import Enum

class SpinnakerBootMessage(object):
    """ A message used for booting the board
    """
    
    class OpCode(Enum):
        HELLO = 0x41
        FLOOD_FILL_START = 0x1
        FLOOD_FILL_BLOCK = 0x3
        FLOOD_FILL_CONTROL = 0x5
    
    def __init__(self, opcode, operand_1, operand_2, operand_3):
        """
        :param opcode: The operation of this packet
        :type opcode: OpCode
        :param operand_1: The first operand
        :type operand_1: int
        :param operand_2: The second operand
        :type operand_2: int
        :param operand_3: The third operand
        :type operand_3: int
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If the\
                    opcode is not a valid value
        """
        pass
