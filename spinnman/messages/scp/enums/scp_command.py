# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from enum import Enum


class SCPCommand(Enum):
    """ The SCP Commands
    """
    CMD_VER = (0, "Get SCAMP Version")
    CMD_RUN = 1
    CMD_READ = (2, "Read SDRAM")
    CMD_WRITE = (3, "Write SDRAM")
    CMD_APLX = 4
    CMD_FILL = 5
    CMD_REMAP = 16
    CMD_LINK_READ = (17, "Read neighbouring chip's memory.")
    CMD_LINK_WRITE = (18, "Write neighbouring chip's memory.")
    CMD_AR = 19
    CMD_NNP = (20, "Send a Nearest-Neighbour packet")
    CMD_P2PC = 21
    CMD_SIG = (22, "Send a Signal")
    CMD_FFD = (23, "Send Flood-Fill Data")
    CMD_AS = 24
    CMD_LED = (25, "Control the LEDs")
    CMD_IPTAG = (26, "Set an IPTAG")
    CMD_SROM = 27
    CMD_ALLOC = (28, "Allocate or Free SDRAM or Routing entries")
    CMD_RTR = (29, "Initialise the router")
    CMD_DPRI = (30, "Dropped Packet Reinjection setup")
    CMD_INFO = (31, "Get Chip Summary Information")
    CMD_BMP_INFO = (48, "Get BMP info structures")
    CMD_FLASH_COPY = 49
    CMD_FLASH_ERASE = 50
    CMD_FLASH_WRITE = 51
    CMD_RESET = 55
    CMD_BMP_POWER = (57, "Turns on or off the machine via BMP")
    CMD_TUBE = 64

    def __new__(cls, value, doc=""):
        # pylint: disable=protected-access, unused-argument
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, doc=""):
        self._value_ = value
        self.__doc__ = doc
