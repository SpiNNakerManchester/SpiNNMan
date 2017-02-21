from enum import Enum

# The default port of the connection
SCP_SCAMP_PORT = 17893

# The default port of the connection
UDP_BOOT_CONNECTION_DEFAULT_PORT = 54321

# The base address of the system variable structure in System ram
SYSTEM_VARIABLE_BASE_ADDRESS = 0xf5007f00

# The base address of a routers diagnostic filter controls
ROUTER_REGISTER_BASE_ADDRESS = 0xe1000000

# The base address of a routers p2p routing table
ROUTER_REGISTER_P2P_ADDRESS = ROUTER_REGISTER_BASE_ADDRESS + 0x10000

# offset for the router filter controls first register (one word each)
ROUTER_FILTER_CONTROLS_OFFSET = 0x200

# point where default filters finish and user set-able ones are available
ROUTER_DEFAULT_FILTERS_MAX_POSITION = 11

# size of a router diagnostic filter control register in bytes
ROUTER_DIAGNOSTIC_FILTER_SIZE = 4

# number of router diagnostic filters
NO_ROUTER_DIAGNOSTIC_FILTERS = 16

# The size of the system variable structure in bytes
SYSTEM_VARIABLE_BYTES = 256

# The max size a UDP packet can be
UDP_MESSAGE_MAX_SIZE = 256

# the amount of size in bytes that the EIEIO command header is
EIEIO_COMMAND_HEADER_SIZE = 3

# The amount of size in bytes the EIEIO data header is
EIEIO_DATA_HEADER_SIZE = 2

# the address of the start of the VCPU structure (copied from sark.h)
CPU_INFO_OFFSET = 0xe5007000

# how many bytes the cpu info data takes up
CPU_INFO_BYTES = 128

# the address at which user0 register starts
CPU_USER_0_START_ADDRESS = 112

# the address at which user0 register starts
CPU_USER_1_START_ADDRESS = 116

# the address at which user0 register starts
CPU_USER_2_START_ADDRESS = 120

# the address at which the iobuf address starts
CPU_IOBUF_ADDRESS_OFFSET = 88

# default UDP tag
DEFAULT_SDP_TAG = 0xFF

# max user requested tag value
MAX_TAG_ID = 7

# The range of values the BMP's 12-bit ADCs can measure.
BMP_ADC_MAX = 1 << 12

# Multiplier to convert from ADC value to volts for lines less than 2.5 V.
BMP_V_SCALE_2_5 = 2.5 / BMP_ADC_MAX

# Multiplier to convert from ADC value to volts for 3.3 V lines.
BMP_V_SCALE_3_3 = 3.75 / BMP_ADC_MAX

# Multiplier to convert from ADC value to volts for 12 V lines.
BMP_V_SCALE_12 = 15.0 / BMP_ADC_MAX

# Multiplier to convert from temperature probe values to degrees Celsius.
BMP_TEMP_SCALE = 1.0 / 256.0

# Temperature value returned when a probe is not connected.
BMP_MISSING_TEMP = -0x8000

# Fan speed value returned when a fan is absent.
BMP_MISSING_FAN = -1

# Additional timeout for BMP power-on commands to reply.
BMP_POWER_ON_TIMEOUT = 10.0

# number of chips to check are booted fully from the middle
NO_MIDDLE_CHIPS_TO_CHECK = 8

# a listing of what spinnaker specific EIEIO commands there are.
EIEIO_COMMAND_IDS = Enum(
    value="EIEIO_COMMAND_IDS",
    names=[
        # Database handshake with external program
        ("DATABASE_CONFIRMATION", 1),

        # Fill in buffer area with padding
        ("EVENT_PADDING", 2),

        # End of all buffers, stop execution
        ("EVENT_STOP", 3),

        # Stop complaining that there is SDRAM free space for buffers
        ("STOP_SENDING_REQUESTS", 4),

        # Start complaining that there is SDRAM free space for buffers
        ("START_SENDING_REQUESTS", 5),

        # Spinnaker requesting new buffers for spike source population
        ("SPINNAKER_REQUEST_BUFFERS", 6),

        # Buffers being sent from host to SpiNNaker
        ("HOST_SEND_SEQUENCED_DATA", 7),

        # Buffers available to be read from a buffered out vertex
        ("SPINNAKER_REQUEST_READ_DATA", 8),

        # Host confirming data being read form SpiNNaker memory
        ("HOST_DATA_READ", 9),

        # command for notifying the external devices that the simulation
        # has stopped
        ("STOP_PAUSE_NOTIFICATION", 10),

        # command for notifying the external devices that the simulation has
        # started
        ("START_RESUME_NOTIFICATION", 11)

    ]
)

# the values used by the SCP iptag time outs. These control how long to wait
# for any message request which requires a response, before raising an error.
# The value is calculated via the following formulae
# 10ms * 2^(tag_timeout_value - 1)
IPTAG_TIME_OUT_WAIT_TIMES = Enum(
    value="IPTAG_TIME_OUT_WAIT_TIMES",
    names=[
        ("TIMEOUT_10_ms", 1),
        ("TIMEOUT_20_ms", 2),
        ("TIMEOUT_40_ms", 3),
        ("TIMEOUT_80_ms", 4),
        ("TIMEOUT_160_ms", 5),
        ("TIMEOUT_320_ms", 6),
        ("TIMEOUT_640_ms", 7),
        ("TIMEOUT_1280_ms", 8),
        ("TIMEOUT_2560_ms", 9)]
)

ROUTER_REGISTER_REGISTERS = Enum(
    value="Registers",
    names=[("LOC_MC", 0),
           ("EXT_MC", 1),
           ("LOC_PP", 2),
           ("EXT_PP", 3),
           ("LOC_NN", 4),
           ("EXT_NN", 5),
           ("LOC_FR", 6),
           ("EXT_FR", 7),
           ("DUMP_MC", 8),
           ("DUMP_PP", 9),
           ("DUMP_NN", 10),
           ("DUMP_FR", 11),
           ("USER_0", 12),
           ("USER_1", 13),
           ("USER_2", 14),
           ("USER_3", 15)]
)
# the types of read available from SARK. These values are used to tell SARK how
# to read the data in a time efficient manner.
READ_TYPES = Enum(
    value="Read_types",
    names=[("BYTE", 0),
           ("HALF_WORD", 1),
           ("WORD", 2)]
)

# This is a mapping between read address in the mapping between word byte
# position, the number of bytes you wish to read, and the type of time
# efficient way to read said amount of bytes via SARK
address_length_dtype = {
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
