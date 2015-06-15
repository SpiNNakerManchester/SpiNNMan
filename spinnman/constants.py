from enum import Enum

# The default port of the connection
SCP_SCAMP_PORT = 17893

# The default port of the connection
UDP_BOOT_CONNECTION_DEFAULT_PORT = 54321

# The base address of the system variable structure in System ram
SYSTEM_VARIABLE_BASE_ADDRESS = 0xf5007f00

# The base address of a routers diagnostic filter controls
ROUTER_REGISTER_BASE_ADDRESS = 0xe1000000

# offset for the router filter controls first register (one word each)
ROUTER_FILTER_CONTROLS_OFFSET = 0x200

# point where default filters finish and user settable ones are available
ROUTER_DEFAULT_FILTERS_MAX_POSITION = 11

# size of a router diagnostic filter control register in bytes
ROUTER_DIAGNOSTIC_FILTER_SIZE = 4

# number of router diagnostic filters
NO_ROUTER_DIAGNOSTIC_FILTERS = 16

# The size of the system variable structure in bytes
SYSTEM_VARIABLE_BYTES = 256

# The max size a udp packet can be
UDP_MESSAGE_MAX_SIZE = 256

# the amount of size in bytes that the EIEIO command header is
EIEIO_COMMAND_HEADER_SIZE = 3

# The amount of size in bytes the EIEIO data header is
EIEIO_DATA_HEADER_SIZE = 2

# how many bytes the cpu info data takes up
CPU_INFO_BYTES = 128

# the address at which user0 register starts
CPU_USER_0_START_ADDRESS = 112

# default udp tag
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

# connection types
CONNECTION_TYPE = Enum(
    value="CONNECTION_TYPE",
    names=[("REVERSE_IPTAG", 0),
           ("SDP_IPTAG", 1),
           ("UDP_BOOT", 2),
           ("UDP_IPTAG", 3),
           ("UDP_SPINNAKER", 4),
           ("UDP_BMP", 5),
           ("USB", 6)])

# types of data that is returned from a bmp_info SCP command.
BMP_INFO_TYPE = Enum(
    value="BMP_INFO_TYPE",
    names=[("SERIAL", 0),
           ("CAN_STATUS", 2),
           ("ADC", 3),
           ("IP_ADDR", 4)])

# types of actions for the leds from a set led request
LEDS_ACTIONS = Enum(
    value="BMP_SET_LED_ACTIONS",
    names=[("ON", 3),
           ("OFF", 2),
           ("TOGGLE", 1)])

# the different types of message types which spinnman supports
TRAFFIC_TYPE = Enum(
    value="TRAFFIC_TYPE",
    names=[("SCP", 0),
           ("SDP", 1),
           ("UDP", 2),
           ("EIEIO_DATA", 3),
           ("EIEIO_COMMAND", 4)])

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

        # Stop complaining that there is sdram free space for buffers
        ("STOP_SENDING_REQUESTS", 4),

        # Start complaining that there is sdram free space for buffers
        ("START_SENDING_REQUESTS", 5),

        # Spinnaker requesting new buffers for spike source population
        ("SPINNAKER_REQUEST_BUFFERS", 6),

        # Buffers being sent from host to SpiNNaker
        ("HOST_SEND_SEQUENCED_DATA", 7),

        # Buffers available to be read from a buffered out vertex
        ("SPINNAKER_REQUEST_READ_DATA", 8),

        # Host confirming data being read form SpiNNaker memory
        ("HOST_DATA_READ", 9)])
