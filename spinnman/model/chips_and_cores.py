class ChipsAndCores(object):
    """ Represents a list of chips and cores on the chips, used to choose a
        subset of the cores on the board where something will happen
    """
    
    def __init__(self, chips_and_cores=None):
        """ 
        :param chips_and_cores: A list of dicts indicating which chips and\
                    cores to get the state of, each with the following keys:
                    * "x": The x-coordinate of a chip
                    * "y": The y-coordinate of a chip
                    * "cores": A list of cores on the chip
        :type chips and cores: dict of {"x": int, "y": int,\
                    "cores": list of int}
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is more than one dict in the list with the same x and y\
                    value
        """
        
    def add_chip_and_cores(self, x, y, cores):
        """ Adds a chip and a set of cores on the chip
        
        :param x: The x-coordinate of a chip
        :type x: int
        :param y: The y-coordinate of a chip
        :type y: int
        :param cores: A list of cores on the chip
        :type cores: list of int
        :return: Nothing is returned
        :rtype: None
        :raise spinnman.exceptions.SpinnmanInvalidParameterException: If there\
                    is already a chip in the list with the same x and y\
                    values
        """
        pass

    def get_chips(self):
        """ Gets a list of the chips and the cores on the chips
        
        :return: The list of chips as a dict, with the following keys:
                    * "x": The x-coordinate of a chip
                    * "y": The y-coordinate of a chip
                    * "cores": A list of cores on the chip
        :rtype chips and cores: dict of {"x": int, "y": int,\
                    "cores": list of int}
        """
        pass
