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
from typing import Dict, Tuple

LOCAL_HOST = "127.0.0.1"

#: the amount of time to wait in seconds between powering off and powering
# on a SpiNNaker board.
POWER_CYCLE_WAIT_TIME_IN_SECONDS: int = 30

#: The default port of the connection
SCP_SCAMP_PORT: int = 17893

#: The default port of the connection
UDP_BOOT_CONNECTION_DEFAULT_PORT: int = 54321

#: The base address of the system variable structure in System ram
SYSTEM_VARIABLE_BASE_ADDRESS: int = 0xf5007f00

#: The base address of a routers diagnostic filter controls
ROUTER_REGISTER_BASE_ADDRESS: int = 0xe1000000

#: The base address of a routers p2p routing table
ROUTER_REGISTER_P2P_ADDRESS: int = ROUTER_REGISTER_BASE_ADDRESS + 0x10000

#: Offset for the router filter controls first register (one word each)
ROUTER_FILTER_CONTROLS_OFFSET: int = 0x200

#: Point where default filters finish and user set-able ones are available
ROUTER_DEFAULT_FILTERS_MAX_POSITION: int = 11

#: Size of a router diagnostic filter control register in bytes
ROUTER_DIAGNOSTIC_FILTER_SIZE: int = 4

#: Number of router diagnostic filters
NO_ROUTER_DIAGNOSTIC_FILTERS: int = 16

#: The size of the system variable structure in bytes
SYSTEM_VARIABLE_BYTES: int = 256

#: The max size a UDP packet can be, excluding headers
UDP_MESSAGE_MAX_SIZE: int = 256

#: The address of the start of the VCPU structure (copied from sark.h)
CPU_INFO_OFFSET: int = 0xe5007000

#: How many bytes the CPU info data takes up
CPU_INFO_BYTES: int = 128

#: The address at which user0 register starts
CPU_USER_START_ADDRESS: int = 112

#: The number of bytes the user start address moves each time
CPU_USER_OFFSET: int = 4

#: The largest user "register" number.
CPU_MAX_USER: int = 3

#: The address at which the iobuf address starts
CPU_IOBUF_ADDRESS_OFFSET: int = 88

#: Max user requested tag value
MAX_TAG_ID: int = 7

#: The range of values the BMP 12-bit ADCs can measure.
BMP_ADC_MAX: int = 1 << 12

#: Multiplier to convert from ADC value to volts for lines less than 2.5 V.
BMP_V_SCALE_2_5: float = 2.5 / BMP_ADC_MAX

#: Multiplier to convert from ADC value to volts for 3.3 V lines.
BMP_V_SCALE_3_3: float = 3.75 / BMP_ADC_MAX

#: Multiplier to convert from ADC value to volts for 12 V lines.
BMP_V_SCALE_12: float = 15.0 / BMP_ADC_MAX

#: Multiplier to convert from temperature probe values to degrees Celsius.
BMP_TEMP_SCALE: float = 1.0 / 256.0

#: Temperature value returned when a probe is not connected.
BMP_MISSING_TEMP: int = -0x8000

#: Fan speed value returned when a fan is absent.
BMP_MISSING_FAN: int = -1

#: Timeout for BMP power-on commands to reply.
BMP_POWER_ON_TIMEOUT: float = 10.0

#: Timeout for other BMP commands to reply
BMP_TIMEOUT: float = 0.5

#: Time to sleep after powering on boards
BMP_POST_POWER_ON_SLEEP_TIME: float = 5.0


class EIEIO_COMMAND_IDS(Enum):
    # pylint: disable=invalid-name
    """
    A listing of what SpiNNaker specific EIEIO commands there are.
    """
    #: Database handshake with external program; not routed via SpiNNaker
    DATABASE = 1
    #: Fill in buffer area with padding
    EVENT_PADDING = 2
    #: End of all buffers, stop execution
    EVENT_STOP = 3
    #: Stop complaining that there is SDRAM free space for buffers
    STOP_SENDING_REQUESTS = 4
    #: Start complaining that there is SDRAM free space for buffers
    START_SENDING_REQUESTS = 5
    #: Spinnaker requesting new buffers for spike source population
    SPINNAKER_REQUEST_BUFFERS = 6
    #: Buffers being sent from host to SpiNNaker
    HOST_SEND_SEQUENCED_DATA = 7
    #: Buffers available to be read from a buffered out vertex
    SPINNAKER_REQUEST_READ_DATA = 8
    #: Host confirming data being read form SpiNNaker memory
    HOST_DATA_READ = 9
    #: Command for notifying the external devices that the simulation
    #: has stopped
    STOP_PAUSE_NOTIFICATION = 10
    #: Command for notifying the external devices that the simulation has
    #: started
    START_RESUME_NOTIFICATION = 11
    #: Host confirming request to read data received
    HOST_DATA_READ_ACK = 12


class IPTAG_TIME_OUT_WAIT_TIMES(Enum):
    # pylint: disable=invalid-name
    """
    The values used by the SCP IP tag time outs. These control how long to wait
    for any message request which requires a response, before raising an error.

    The value is calculated via the following formula:

    10ms * 2^(`tag_timeout_value` - 1)
    """
    TIMEOUT_10_ms = 1
    TIMEOUT_20_ms = 2
    TIMEOUT_40_ms = 3
    TIMEOUT_80_ms = 4
    TIMEOUT_160_ms = 5
    TIMEOUT_320_ms = 6
    TIMEOUT_640_ms = 7
    TIMEOUT_1280_ms = 8
    TIMEOUT_2560_ms = 9


class ROUTER_REGISTER_REGISTERS(Enum):
    # pylint: disable=invalid-name
    """
    The indices to the router registers.
    """
    LOC_MC = 0
    EXT_MC = 1
    LOC_PP = 2
    EXT_PP = 3
    LOC_NN = 4
    EXT_NN = 5
    LOC_FR = 6
    EXT_FR = 7
    DUMP_MC = 8
    DUMP_PP = 9
    DUMP_NN = 10
    DUMP_FR = 11
    USER_0 = 12
    USER_1 = 13
    USER_2 = 14
    USER_3 = 15


class READ_TYPES(Enum):
    # pylint: disable=invalid-name
    """
    The types of read available from SARK. These values are used to tell
    SARK how to read the data in a time efficient manner.
    """
    BYTE = 0
    HALF_WORD = 1
    WORD = 2


#: This is a mapping between read address in the mapping between word byte
#: position, the number of bytes you wish to read, and the type of time
#: efficient way to read said amount of bytes via SARK
address_length_dtype: Dict[Tuple[int, int], READ_TYPES] = {
    (0, 0): READ_TYPES.WORD,
    (0, 1): READ_TYPES.BYTE,
    (0, 2): READ_TYPES.HALF_WORD,
    (0, 3): READ_TYPES.BYTE,
    (1, 0): READ_TYPES.BYTE,
    (1, 1): READ_TYPES.BYTE,
    (1, 2): READ_TYPES.BYTE,
    (1, 3): READ_TYPES.BYTE,
    (2, 0): READ_TYPES.HALF_WORD,
    (2, 1): READ_TYPES.BYTE,
    (2, 2): READ_TYPES.HALF_WORD,
    (2, 3): READ_TYPES.BYTE,
    (3, 0): READ_TYPES.BYTE,
    (3, 1): READ_TYPES.BYTE,
    (3, 2): READ_TYPES.BYTE,
    (3, 3): READ_TYPES.BYTE}

#: This is the default timeout when using SCP
SCP_TIMEOUT: float = 1.0

#: This is the default timeout when using SCP count (can take a bit longer)
SCP_TIMEOUT_COUNT = 5.0

#: This is the default number of retries when using SCP
N_RETRIES: int = 10

#: This is the number of retries during boot - this is different because
#: otherwise boot takes too long (retrying on a non-booted machine will never
#: work)
BOOT_RETRIES: int = 3
