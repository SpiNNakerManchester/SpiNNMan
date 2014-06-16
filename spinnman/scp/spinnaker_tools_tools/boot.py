__author__ = 'stokesa6'
#
# DESCRIPTION
#   Boot API required to load SpiNNaker with an operating system (such as SC&MP)
#
# AUTHORS
#   Kier J. Dugan - (kjd1v07@ecs.soton.ac.uk)
#   Andrew Roley ()
#   Alan Barry Stokes (stokesa6@cs.man.ac.uk)
#
#
# COPYRIGHT
#   Copyright (c) 2012 The University of Southampton.  All Rights Reserved.
#   Electronics and Electrical Engingeering Group,
#   School of Electronics and Computer Science (ECS)
#

# imports
import socket, struct, time, re, numpy, sys, getopt
from SpiNNMan.spinnman.scp.spinnaker_tools_tools import scamp_constants
from SpiNNMan.spinnman.scp.scp_connection import SCPConnection
from SpiNNMan.spinnman.scp.scp_message import SCPMessage
from SpiNNMan.spinnman import spinnman_exceptions


__all__ = ['boot', 'readstruct' ]

# functions
def _readstruct(section_name, structfile):
    """ reads a specific section of a structfile
    :param section_name: a section to read from a fiven structfile
    :param structfile: a structfile to read from
    :type section_name: str
    :type structfile: str or file
    :return: a dictonary which contains elements of the structfile
    :rtype: dict
    :raises: spinnman.spinnman_exceptions.BootError when given a malformed
             struct file
    """
    sv = dict()
    sv['=size='] = 0;
    match = False
    matchFound = False
    for line in open(structfile):
        line = line.strip()
        comment_idx = line.find("#")
        if comment_idx != -1:
            line = line[:comment_idx].strip()
        if line != "":
            equal_match = re.match("(^[^\s]+) = ([^\s]+)$", line)
            if equal_match != None:
                if equal_match.group(1) == "name":
                    if equal_match.group(2) == section_name:
                        match = True
                        matchFound = True
                    else:
                        match = False
            if match == True:
                if equal_match != None:
                    if equal_match.group(1) == "size":
                        sv['=size='] = int(equal_match.group(2), 0)
                    elif equal_match.group(1) == "base":
                        sv['=base='] = int(equal_match.group(2), 0)
                    elif equal_match.group(1) != "name":
                        raise spinnman_exceptions.\
                            BootError("Unrecognised line in %s - "
                                      "unrecognised item %s from line: "
                                      "%s" % (structfile,
                                              equal_match.group(1), line))

                else:
                    line_match = re.match("^([\w\.]+)"
                                          "(\[\d+\])"
                                          "?\s+(V|v|C|A16)"
                                          "\s+(\S+)"
                                          "\s+(%\d*[dx]|%s)\s+(\S+)$", line)
                    if line_match != None:
                        (name, index, pack,
                         offset, fmt, value) = line_match.groups()
                        offset = int(offset, 0)
                        value = int(value, 0)
                        if index != None and index != "":
                            index = int(("%s" % index)[1:-1])
                            sv[name] = [value, pack, offset, fmt, index]
                        else:
                            sv[name] = [value, pack, offset, fmt, 1]
                    else:
                        raise spinnman_exceptions.\
                            BootError("Unrecognised line in %s - format does"
                                      " not match expected format: %s"
                                      % (structfile, line))
    if matchFound == False:
        raise spinnman_exceptions.BootError("Missing section %s in %s"
                                            % (section_name, structfile))

def _readconf(sv, configfile):
    """ reads a config file
    :param sv: a dictonary object to store elements from the config file in
    :param configfile: the config file to read
    :type sv: dict
    :type configfile: str or file
    :return: the inputted dict with added elements from the configfile
    :rtype: dict
    :raises: spinnman.spinnman_exceptions.BootError when given a malformed
             config file
    """
    for line in open(configfile):
        line = line.strip()
        comment_idx = line.find("#")
        if comment_idx != -1:
            line = line[:comment_idx].strip()
        if line != "":
            config_match = re.match("^([\w\.]+)"
                                    "\s+(0x[0-9a-fA-F]+|\d+|time)$", line)
            if config_match != None:
                (name, value) = config_match.groups()
                if name in sv:
                    if value == "time":
                        value = time.time()
                    sv[name][0] = int(value, 0)
            else:
                raise spinnman_exceptions.BootError("Unrecognised line in %s - "
                                                    "format does not match "
                                                    "expected format: %s"
                                                    % (configfile, line))


def _pack(sv, data, dataoffset, sizelimit):
    """ packs data into a form usable in packets
    :param sv: the dictonary that contains elements from the config and struct
               files
    :param data: data which should be packed
    :param dataoffset: how far into the packing that the data should start being
                       written
    :param sizelimit: the size limit of the packed data
    :type sv: dict
    :type data: numpy array
    :type dataoffset: int
    :type sizelimit: int
    :return: None
    :rtype: None
    ABS(Is this correct? as you pack somethign but dont
        get the packed version back?)
    :raises: spinnman.spinnman_exceptions.StructInterpertationException if the
             method cannot decide on how to pack the data
    """
    for field in sv:
        if not field.startswith("="):
            (value, pack, offset) = sv[field][0:3]
            if offset < sizelimit and value != "-":
                if pack == "V":
                    pack = "<I"
                elif pack == "v":
                    pack = "<H"
                elif pack == "C":
                    pack = "B"
                elif pack == "A16":
                    pack = "16s"
                else:
                    raise spinnman_exceptions.\
                        StructInterpertationException("Unrecognised pack format"
                                                      " %s" % pack)
                struct.pack_into(pack, data, dataoffset + offset, value)

def _boot_pkt(socket, host, op, a1, a2, a3, data = None, offset = 0,
             datasize = 0):
    """private method that sends the boot command down to the spinnaker machine
    :param socket: stream to write the command to
    :param host: hostname of the target SpiNNaker
    :param op: boot ROM command
    :param a1: argument 1 -- varies with ``op``
    :param a2: argument 2 -- varies with ``op``
    :param a3: argument 3 -- varies with ``op``
    :param data: optional data
    :param offset: the offset into the data to start from
    :param datasize: the maximum amount of data to write from the data
    :type socket: socket.socket
    :type host: str
    :type op: boot constant from scamp_constants
    :type a1: int
    :type a2: int
    :type a3: int
    :type data: numpy array or None
    :type offset: int
    :type datasize: int
    :return: None
    :rtype: None
    :raises: None: does not raise any known exceptions
    """
    if data != None:
        pkt_data = numpy.zeros(datasize + 18, dtype=numpy.uint8)
        struct.pack_into(">HLLLL", pkt_data, 0, scamp_constants.BOOT_PROT_VER,
                         op, a1, a2, a3)
        off = 0
        readsize = datasize
        if (offset + readsize) > data.size:
            readsize = data.size - offset
        while off < readsize:
            the_word = struct.unpack_from("<I", data, offset + off)[0]
            struct.pack_into(">I", pkt_data, 18 + off, the_word)
            off += 4
        socket.sendto(pkt_data, (host, scamp_constants.BOOT_PORT))
    else:
        hdr = struct.pack(">HLLLL", scamp_constants.BOOT_PROT_VER, op, a1,
                          a2, a3)
        socket.sendto(hdr, (host, scamp_constants.BOOT_PORT))
    time.sleep(scamp_constants.BOOT_DELAY)

def _rom_boot(hostname, data):
    """sends the boot rom to the spinnaker machine listening on the hostname
    :param hostname:
    :param data:
    :type hostname: str
    :type data: numpy array or None
    :return: None
    :rtype: None
    :raises: spinnMan.spinnman_exceptions.BootException
    """
    # determine the number of blocks required to send the boot file
    block_size  = scamp_constants.BOOT_BLOCK_SIZE * 4 # convert into bytes from words
    block_count = (data.size + block_size - 1) / block_size # implicit modulo

    # make sure the boot file is not larger than the TCRAM
    if block_count > scamp_constants.BOOT_MAX_BLOCKS:
        raise spinnman_exceptions.BootError("Boot file is too large "
                                            "and will not fit in DTCM.")

    # attempt to open a socket to the remote host
    host = socket.gethostbyname (hostname)
    sock = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    _boot_pkt(sock, host, scamp_constants.BOOT_CMD_START, 0, 0, block_count - 1)
    offset = 0
    for cur_block in range(0, block_count):
        arg1 = ((scamp_constants.BOOT_BLOCK_SIZE - 1) << 8) | cur_block
        _boot_pkt(sock, host, scamp_constants.BOOT_CMD_BLOCK, arg1, 0,  0,
                  data, offset, block_size)
        offset += block_size
    _boot_pkt(sock, host, scamp_constants.BOOT_CMD_DONE, 1, 0, 0)

def boot(hostname, bootfile, configfile, structfile):
    """ entrance function to the boot system
    :param hostname: the name of the machine in ip format or equivalent
    :param bootfile: the filepath to the boot file used during this boot seq
    :param configfile: the filpath of the config file used during this boot seq
    :param structfile: the filepath of the struct file used during this boot seq
    :type hostname: str
    :type bootfile: str
    :type configfile: str
    :type structfile: str
    :return: None
    :rtype: None
    :raises:spinnMan.spinnman_exceptions.BootException
    """
    sv = _readstruct("sv", structfile)
    _readconf(sv, configfile)
    buf = numpy.fromfile(file=bootfile, dtype=numpy.uint8)
    current_time = time.time()
    sv["unix_time"][0] = current_time
    sv["boot_sig"][0] = current_time

    if bootfile.endswith(".boot"):
        sv["root_chip"][0] = 1
        _pack(sv, buf, 384, 128)
        _rom_boot(hostname, buf)

    elif bootfile.endswith(".aplx"):
        sv["boot_delay"][0] = 0
        _pack(sv, buf, 384, 128)

    else:
        raise spinnman_exceptions.BootError("Unknown file extension of boot "
                                            "file %s" % bootfile)

def reset(hostname):
    """ Establishes a SCP connection to the board-management processor specified
    by ``hostname`` and sends a reset command.
    .. warning::

        This function is only applicable to SpiNN-4 (or greater) boards that
        have board-management processors on the PCB. yet does not check that the
        board commincating with the given hostname is a spinn-4 or spinn-5 board

    :param hostname: hostname of the board-management processor of the target
                     SpiNNaker
    :type hostname: str
    :return: None
    :rtype: None
    :raises: None: does not raise any known exceptions
    """
    conn = SCPConnection(hostname)
    msg        = SCPMessage()
    msg.cmd_rc = scamp_constants.CMD_RESET
    msg.arg1   = 2
    conn.send_scp_msg (msg)

def _printargs():
    """helper method which prints out the order and explination of the boot args
    :return: None
    :rtype: None
    :raises: None: does not raise any known exceptions
    """
    print sys.argv[0], " ", "-h <hostname> -b <bootfile> -c <configfile> -s " \
                            "<structfile>"
    sys.exit(2)

"""entrance method when called directly"""
if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?h:b:c:s:", \
            ["hostname=", "bootfile=", "configfile=", "structfile="])
    except getopt.GetoptError:
        _printargs()
    hostname = None
    bootfile = None
    configfile = None
    structfile = None
    for opt, arg in opts:
        if opt == "-?":
            _printargs()
        elif opt in ("-h", "--hostname"):
            hostname = arg
        elif opt in ("-b", "--bootfile"):
            bootfile = arg
        elif opt in ("-c", "--configfile"):
            configfile = arg
        elif opt in ("-s", "--structfile"):
            structfile = arg
    if (hostname == None) or (bootfile == None) or (configfile == None) or\
       (structfile == None):
        print "Missing arguments:"
        _printargs()
    boot(hostname, bootfile, configfile, structfile)
