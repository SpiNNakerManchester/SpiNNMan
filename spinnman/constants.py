from enum import Enum
# The default port of the connection
SCP_SCAMP_PORT = 17893

# The default port of the connection
UDP_BOOT_CONNECTION_DEFAULT_PORT = 54321

# The base address of the system variable structure in System ram
SYSTEM_VARIABLE_BASE_ADDRESS = 0xf5007f00

# The base address of a routers dianostic filter controls
ROUTER_REGISTER_BASE_ADDRESS = 0xe1000000
#offset for the router register
ROUTER_FILTER_CONTROLS_OFFSET = 0x200
#point where default filters finish and user settable ones are avilable
ROUTER_DEFAULT_FILTERS_MAX_POSITION = 11
#size of a router dianostic
ROUTER_DIAGNOSTIC_FILTER_SIZE = 1 # in words

#number of router dianostic filters
NO_ROUTER_DIAGNOSTIC_FILTERS = 16

# The size of the system variable structure in bytes
SYSTEM_VARIABLE_BYTES = 256

# The max size a udp packet can be
UDP_MESSAGE_MAX_SIZE = 256
EIEIO_COMMAND_HEADER_SIZE = 3
EIEIO_DATA_HEADER_SIZE = 2


#how many bytes the cpu info data takes up
CPU_INFO_BYTES = 128

# the address at which user0 register starts
CPU_USER_0_START_ADDRESS = 112

#default udp tag
DEFAULT_SDP_TAG = 0xFF

#connection types
CONNECTION_TYPE = Enum(
    value="CONNECTION_TYPE",
    names=[("REVERSE_IPTAG", 0),
           ("SDP_IPTAG", 1),
           ("UDP_BOOT", 2),
           ("UDP_IPTAG", 3),
           ("UDP_SPINNAKER", 4),
           ("USB", 5)])

TRAFFIC_TYPE = Enum(
    value="TRAFFIC_TYPE",
    names=[("SCP", 0),
           ("SDP", 1),
           ("UDP", 2),
           ("EIEIO_DATA", 3),
           ("EIEIO_COMMAND", 4)])

EIEIO_COMMAND_IDS = Enum(
    value="EIEIO_COMMAND_IDS",
    names=[("BUFFER_MANAGEMENT", 0),
           ("DATABASE_CONFIRMATION", 1)])

RECEIVED_BUFFER_COMMAND_IDS = Enum(
    value="RECEIVED_BUFFER_COMMAND_IDS",
    names=[("BUFFER_RECIEVE", 1),
           ("BUFFER_SEND", 2)])

SENT_BUFFER_COMMAND_IDS = Enum(
    value="SENT_BUFFER_COMMAND_IDS",
    names=[("NEW_BUFFERS", 1),
           ("STOP_SENDING_REQUESTS", 2),
           ("START_SENDING_REQUESTS", 3),
           ("READ_DATA", 4)])