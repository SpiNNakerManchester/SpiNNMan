"""constants file for all scamp based message codes etc"""
#
# DESCRIPTION
# Defines the various constants that are used by SC&MP 1.02.
#
# AUTHORS
# Kier J. Dugan - (kjd1v07@ecs.soton.ac.uk)
# Alan Barry Stokes (stokesa6@cs.man.ac.uk)
#
#
# COPYRIGHT
# Copyright (c) 2012 The University of Southampton. All Rights Reserved.
# Electronics and Electrical Engingeering Group,
# School of Electronics and Computer Science (ECS)
#


# constants

# SC&MP command codes
CMD_VER = 0
CMD_RUN = 1
CMD_READ = 2
CMD_WRITE = 3
CMD_APLX = 4
CMD_FILL = 5
CMD_REMAP = 16
CMD_LINK_READ = 17
CMD_LINK_WRITE = 18
CMD_AR = 19
CMD_NNP = 20
CMD_P2PC = 21
CMD_SIG = 22
CMD_FFD = 23
CMD_AS = 24
CMD_LED = 25
CMD_IPTAG = 26
CMD_SROM = 27
CMD_FLASH_COPY = 49
CMD_FLASH_ERASE = 50
CMD_FLASH_WRITE = 51
CMD_RESET = 55
CMD_POWER = 57
CMD_TUBE = 64

# Nearest-neighbour constants
NN_CMD_SIG0 = 0
NN_CMD_RTRC = 1
NN_CMD_LTPC = 2
NN_CMD_SP_3 = 3
NN_CMD_SIG1 = 4
NN_CMD_P2PC = 5
NN_CMD_FFS = 6
NN_CMD_SP_7 = 7
NN_CMD_PING = 8
NN_CMD_P2PB = 9
NN_CMD_SDP = 10
NN_CMD_SP_11 = 11
NN_CMD_FBS = 12
NN_CMD_FBD = 13
NN_CMD_FBE = 14
NN_CMD_FFE = 15

# Data sizes
TYPE_BYTE = 0
TYPE_HALF = 1
TYPE_WORD = 2

# IP tag definitions
IPTAG_NEW = 0
IPTAG_SET = 1
IPTAG_GET = 2
IPTAG_CLR = 3
IPTAG_TTO = 4

IPTAG_VALID = 0x8000   # Entry is valid
IPTAG_TRANS = 0x4000   # Entry is transient
IPTAG_ARP = 0x2000   # Awaiting ARP resolution

IPTAG_NONE = 255   # Invalid tag/transient request
IPTAG_HOST = 0   # Reserved for host

# response codes
RC_OK = 0x80   # Command completed OK
RC_LEN = 0x81   # Bad packet length
RC_SUM = 0x82   # Bad checksum
RC_CMD = 0x83   # Bad/invalid command
RC_ARG = 0x84   # Invalid arguments
RC_PORT = 0x85   # Bad port number
RC_TIMEOUT = 0x86   # Timeout
RC_ROUTE = 0x87   # No P2P route
RC_CPU = 0x88   # Bad CPU number
RC_DEAD = 0x89   # SHM dest dead
RC_BUF = 0x8a   # No free SHM buffers
RC_P2P_NOREPLY = 0x8b   # No reply to open
RC_P2P_REJECT = 0x8c   # Open rejected
RC_P2P_BUSY = 0x8d   # Dest busy
RC_P2P_TIMEOUT = 0x8e   # Dest died?
RC_PKT_TX = 0x8f   # Pkt Tx failed

SDP_DATA_SIZE = 256   # max. payload size of SDP packet

# led control flags
LED_NO_CHANGE = 0
LED_INVERT = 1
LED_OFF = 2
LED_ON = 3

# state ids
PROCESSOR_DEAD = 0
PROCESSOR_PWRDN = 1
PROCESSOR_RTE = 2
PROCESSOR_WDOG = 3
PROCESSOR_INIT = 4
PROCESSOR_READY = 5
PROCESSOR_C_MAIN = 6
PROCESSOR_RUN = 7
PROCESSOR_SYNC0 = 8
PROCESSOR_SYNC1 = 9
PROCESSOR_PAUSE = 10
PROCESSOR_EXIT = 11
PROCESSOR_IDLE = 12

#signals
SIGNAL_INIT = 0
SIGNAL_PWRDN = 1
SIGNAL_STOP = 2
SIGNAL_START = 3
SIGNAL_SYNC0 = 4
SIGNAL_SYNC1 = 5
SIGNAL_PAUSE = 6
SIGNAL_CONT = 7
SIGNAL_EXIT = 8
SIGNAL_TIMER = 9
SIGNAL_USR0 = 10
SINGAL_USR1 = 11
SIGNAL_USR2 = 12
SIGNAL_USR3 = 13
SIGNAL_OR = 16
SIGNAL_AND = 17
SIGNAL_COUNT = 18

rc_map = {0x80: ('RC_OK', 'Command completed OK'),
          0x81: ('RC_LEN', 'Bad packet length'),
          0x82: ('RC_SUM', 'Bad checksum'),
          0x83: ('RC_CMD', 'Bad/invalid command'),
          0x84: ('RC_ARG', 'Invalid arguments'),
          0x85: ('RC_PORT', 'Bad port number'),
          0x86: ('RC_TIMEOUT', 'Timeout'),
          0x87: ('RC_ROUTE', 'No P2P route'),
          0x88: ('RC_CPU', 'Bad CPU number'),
          0x89: ('RC_DEAD', 'SHM dest dead'),
          0x8a: ('RC_BUF', 'No free SHM buffers'),
          0x8b: ('RC_P2P_NOREPLY', 'No reply to open'),
          0x8c: ('RC_P2P_REJECT', 'Open rejected'),
          0x8d: ('RC_P2P_BUSY', 'Dest. busy'),
          0x8e: ('RC_P2P_TIMEOUT', 'Dest. not responding'),
          0x8f: ('RC_PKT_TX', 'Packet tx. failed')}

cc_map = {CMD_VER: 'CMD_VER',
          CMD_RUN: 'CMD_RUN',
          CMD_READ: 'CMD_READ',
          CMD_WRITE: 'CMD_WRITE',
          CMD_APLX: 'CMD_APLX',
          CMD_FILL: 'CMD_FILL',
          CMD_REMAP: 'CMD_REMAP',
          CMD_LINK_READ: 'CMD_LINK_READ',
          CMD_LINK_WRITE: 'CMD_LINK_WRITE',
          CMD_AR: 'CMD_AR',
          CMD_NNP: 'CMD_NNP',
          CMD_P2PC: 'CMD_P2PC',
          CMD_SIG: 'CMD_SIG',
          CMD_FFD: 'CMD_FFD',
          CMD_AS: 'CMD_AS',
          CMD_LED: 'CMD_LED',
          CMD_IPTAG: 'CMD_IPTAG',
          CMD_SROM: 'CMD_SROM',
          CMD_FLASH_COPY: 'CMD_FLASH_COPY',
          CMD_FLASH_ERASE: 'CMD_FLASH_ERASE',
          CMD_FLASH_WRITE: 'CMD_FLASH_WRITE',
          CMD_RESET: 'CMD_RESET',
          CMD_TUBE: 'CMD_TUBE'}

nn_cc_map = {NN_CMD_FFS: 'NN_CMD_FFS',
             NN_CMD_FFE: 'NN_CMD_FFE'}

# boot constants
BOOT_PORT = 54321
BOOT_DELAY = 0.01
BOOT_PROT_VER = 1
BOOT_BLOCK_SIZE = 256   # words (i.e. 1024 bytes)
BOOT_MAX_BLOCKS = 32
BOOT_CMD_START = 1
BOOT_CMD_BLOCK = 3
BOOT_CMD_DONE = 5