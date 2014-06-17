__author__ = 'stokesa6'

import logging
import math
import os
import subprocess
from spinnman import spinnman_exceptions
logger = logging.getLogger(__name__)


class TranscieverUtilities(object):
    """ class object that contains a collection of utility functions used by \
        the transciever during its execution
    """
    
    def __init__(self):
        """
        :return: a TranscieverUtilities object
        :rtype: Spinnman.interfaces.transceiver_tools.TranscieverUtilities\
                object
        :raise: None: does not raise any known exceptions
        """
        logger.debug("initlising a utility object for scp")

    @staticmethod
    def send_ybug_command(hostname, command_string):
        """Create an instance of `ybug` and use it to execute the given command\
           string.
           :param hostname: the name of a spinnaker machine
           :param command_string: the command and its args in a string format
           :type hostname: str
           :type command_string: str
           :return: None
           :rtype: None
           :raise: Spinnman.spinnman_exceptions.ybug_exception
        """
        logger.warn("USING YBUG DIRECTLY IS NOT RECOMMENDED. PLEASE USE THE "
                    "TRANSCIEVER INTERFACE INSTEAD")
        p = subprocess.Popen(["ybug", hostname], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = p.communicate(command_string + "\nquit")
    
        if "error" in out:
            raise Exception("STDOUT=\n%s\n\nSTDERR=\n%s" % (out, err))

    def parse_region(self, region, chip_x, chip_y):
        """takes a region and checks its in the correct format and converts if \
           needed
           :param region: a region definition
           :param chip_x: a id for a chip in the x dimension
           :param chip_y: a id for a chip in the y dimenison
           :type region: str
           :type chip_x: int
           :type chip_y: int
           :return a region in a format recogonised by the sark
           :rtype: int
           :raise: Spinnman.spinnman_exceptions.SpinnmanException
        """
        # if no region defined, return 0
        if region is None:
            raise spinnman_exceptions.SpinnmanException("no region was defined")

        # if current region
        if region == "." or str(region).partition(",")[1] == ",":
            # if no x and y corrds defined, return 0
            if chip_x is None and chip_y is None:
                raise spinnman_exceptions.\
                    SpinnmanException("no chip coords were "
                                      "supplied for parsing region")
            else:
                # return some number (no idea what this actually computes)
                m = (chip_y & 3) * 4 + (chip_x & 3)
                return ((chip_x & 252) << 24) + ((chip_y & 252) << 16) + \
                       (3 << 16) + (1 << m)

        # if a region defined as a coord
        if str(region).partition(",")[1] == ",":
            bits = str(region).partition(",")
            x = int(bits[0])
            y = int(bits[2])
            m = (x & 3) * 4 + (y & 3)
            return ((x & 252) << 24) + ((y & 252) << 16) + (3 << 16) + (1 << m)

        # if all is defined, change to 0-15
        if region.lower() == "all":
            region = "0-15"

        #check that the region is in the correct format
        region_bits = region.split(".")
        number_of_levels = len(region_bits) - 1
        if number_of_levels < 0 or number_of_levels > 3:
            raise spinnman_exceptions.\
                SpinnmanException("the region given did not have enough levels")

        x, y = 0, 0
        for level in range(number_of_levels):
            d = int(region_bits[level])
            if d > 15 or d < 0:
                raise spinnman_exceptions.\
                    SpinnmanException("the region requested does not exist. "
                                      "out of bounds")

            shift = 6 - 2 * level

            x += (d & 3) << shift
            y += (d >> 2) << shift

        mask = self.parse_bits(region_bits[-1], 0, 15)

        if mask is None:
            raise spinnman_exceptions.SpinnmanException("no mask was supplied "
                                                        "for parsing a region")

        return (x << 24) + (y << 16) + (number_of_levels << 16) + mask

    @staticmethod
    def parse_apps(app_id, app_range):
        """ parse a appid and a app range into somethign sark can understand

        :param app_id: the basic app_id
        :param app_range: the rnage from the app_id to which to parse
        :type app_id: int
        :type app_range: int
        :return merged app_id range
        :rtype: int
        :raise: Spinnman.spinnman_exceptions.SpinnmanException
        """
        if app_range is None:
            return 255
        elif app_range < 1:
            raise spinnman_exceptions.SpinnmanException("range is less than 1, "
                                                        "a app region must be "
                                                        "positive")
        elif app_id % app_range != 0:
            raise spinnman_exceptions.SpinnmanException("range % app_id "
                                                        "must equal 0")
        elif app_id + app_range > 255:
            raise spinnman_exceptions.SpinnmanException("range + app_id must "
                                                        "not go above 255")
        return 255 & ~(app_range - 1)

    @staticmethod
    def parse_bits(mask, min_core_id, max_core_id):
        """parses the bits or converts if required

        :param mask: the mask
        :param min_core_id: the minimum core id to parse
        :param max_core_id: the maximum core id to parse
        :type mask: str
        :type min_core_id: int
        :type max_core_id: int
        :return a parsed core
        :rtype: int
        :raise: Spinnman.spinnman_exceptions.SpinnmanException
        """
        if mask is None:
            raise spinnman_exceptions.SpinnmanException("no mask was supplied "
                                                        "for parsing a region")
        if mask.lower() == "all":
            mask = "{}-{}".format(min_core_id, max_core_id)

        node_range = mask.split(",")
        mask = 0
        for sub in node_range:
            if sub.isdigit():
                if int(sub) < min_core_id or int(sub) > max_core_id:
                    return 0
                else:
                    mask |= 1 << int(sub)
            else:
                bits = sub.split("-")
                if len(bits) == 2:
                    l, h = bits[0], bits[1]
                    if int(l) > int(h) or int(l) < min_core_id or\
                       int(h) > max_core_id:
                        return 0
                    else:
                        for i in range(int(l), int(h)+1):
                            mask |= 1 << i
                else:
                    return 0
        return mask

    def parse_cores(self, cores):
        """parses cores by bit

        :param cores: the cores to parse
        :type cores: str
        :return: parsed cores
        :rtype: str
        :raise Spinnman.spinnman_exceptions.SpinnmanException
        """
        return self.parse_bits(cores, 1, 17)

    @staticmethod
    def read_file(file_name, max_length=65536):
        """reads a binary file to convert to memory for the scp messages

        :param file_name: the file path to read in
        :param max_length: the max length of data that can be read in and \
                           loaded on a chip
        :type file_name: str
        :type max_length: int
        :return string array containing the contents of the file
        :rtype: str array
        :raise: Spinnman.spinnman_exceptions.SpinnmanException
        """
        statinfo = os.stat(file_name)
        if statinfo.st_size >= max_length:
            raise spinnman_exceptions.SpinnmanException("file too big to "
                                                        "be written to a core")
        try:
            opened_file = open(file_name, 'rb')
            buf = opened_file.read(statinfo.st_size)
            opened_file.close()
            return buf
        except IOError:
            print "failed to read the file at {}".format(file_name)

    @staticmethod
    def calculate_region_id(x, y):
        """takes an x and y coord and creates a region id for it

        :param x: id of a chip in x dimension
        :param y: id of a chip in y dimension
        :type x: int
        :type y: int
        :return a region id in string format
        :rtype: str
        :raise: None: does not raise any known exceptions
        """
        level_0 = 4 * (math.floor(y / 64))
        level_0 += math.floor(x / 64)
        x_offset = x - (64 * math.floor(x / 64))
        y_offset = y - (64 * math.floor(y / 64))
        level_1 = 4 * (math.floor(y_offset / 16))
        level_1 += math.floor(x_offset / 16)
        x_offset -= 16 * math.floor(x_offset / 16)
        y_offset -= 16 * math.floor(y_offset / 16)
        level_2 = 4 * (math.floor(y_offset / 4))
        level_2 += math.floor(x_offset / 4)
        x_offset -= 4 * math.floor(x_offset / 4)
        y_offset -= 4 * math.floor(y_offset / 4)
        level_3 = 4 * (math.floor(y_offset / 1))
        level_3 += math.floor(x_offset / 1)
        return "{}.{}.{}.{}".format(int(level_0), int(level_1),
                                    int(level_2), int(level_3))
