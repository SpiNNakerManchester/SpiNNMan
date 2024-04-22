# Copyright (c) 2014 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum


class SCPCommand(Enum):
    """
    The SCP Commands.
    """
    # ======== SARK ========
    #: Get software version.
    CMD_VER = 0
    CMD_RUN = 1
    #: Read SDRAM.
    CMD_READ = 2
    #: Write SDRAM.
    CMD_WRITE = 3
    CMD_APLX = 4
    CMD_FILL = 5
    # ======== SCAMP ========
    CMD_COUNT = 15
    CMD_REMAP = 16
    #: Read neighbouring chip's memory.
    CMD_LINK_READ = 17
    #: Write neighbouring chip's memory.
    CMD_LINK_WRITE = 18
    CMD_AR = 19
    #: Send a Nearest-Neighbour packet.
    CMD_NNP = 20
    #: Copy a binary from an adjacent chip and start it
    CMD_APP_COPY_RUN = 21
    #: Send a Signal.
    CMD_SIG = 22
    #: Send Flood-Fill Data.
    CMD_FFD = 23
    CMD_AS = 24
    #: Control the LEDs.
    CMD_LED = 25
    #: Set an IPTAG.
    CMD_IPTAG = 26
    CMD_SROM = 27
    #: Allocate or Free SDRAM or Routing entries.
    CMD_ALLOC = 28
    #: Initialise the router.
    CMD_RTR = 29
    #: Dropped Packet Reinjection setup.
    CMD_DPRI = 30
    #: Get Chip Summary Information.
    CMD_INFO = 31
    #: Control sending of synchronisation messages.
    CMD_SYNC = 32

    # ======== BMP ========
    #: Get BMP info structures
    CMD_BMP_INFO = 48
    CMD_FLASH_COPY = 49
    CMD_FLASH_ERASE = 50
    CMD_FLASH_WRITE = 51
    CMD_RESET = 55
    #: Turns on or off the machine via BMP.
    CMD_BMP_POWER = 57

    # ======== OUTBOUND (OBSOLETE) ========
    CMD_TUBE = 64
