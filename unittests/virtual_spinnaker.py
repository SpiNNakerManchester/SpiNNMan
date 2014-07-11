__author__ = 'Petrut'
import socket
from spinn_machine import processor as proc , link as link , sdram as sdram, router as router, chip as chip
import spinn_machine.exceptions as exc
import spinn_machine.machine as machine
import logging
import time
import spinnman.messages.scp_message as scp_message
import spinnman.messages.scp_command as scp_cmd
import spinnman.messages.sdp_flag as sdp_flg

class VirtualSpiNNaker(machine.Machine):

    def __init__(self, host, port):
        flops = 1000
        (E, NE, N, W, SW, S) = range(6)

        processors = list()
        for i in range(18):
            processors.append(proc.Processor(i, flops))

        links = list()
        links.append(link.Link(0,0,0,0,1,S,S))

        SDRAM = sdram.SDRAM(128)

        links = list()

        links.append(link.Link(0,0,0,1,1,N,N))
        links.append(link.Link(0,1,1,1,0,S,S))
        links.append(link.Link(1,1,2,0,0,E,E))
        links.append(link.Link(1,0,3,0,1,W,W))
        r = router.Router(links,False,100,1024)

        ip = "127.0.0.1"
        chips = list()
        for x in range(5):
            for y in range(5):
                chips.append(chip.Chip(x,y,processors,r,SDRAM,ip))

        super(VirtualSpiNNaker,self).__init__(chips)

        self.host = host#'localhost'
        self.port = port#17893
        print "Booting vSpiNNaker"
        self._record = False
        self.my_socket = socket.socket(type= socket.SOCK_DGRAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.my_socket.bind((self.host,self.port))
        #my_socket.listen(1)
        msg = "Everything set up. Listening for connection on port " + str(self.port) +  "."
        print msg


    def rcv(self):
        while True:
            self.receive_message()

    def receive_message(self):
        data, addr = self.my_socket.recvfrom(self.port)
        print "ADDRESS -----------------------",addr
        self.my_socket.sendto(data, addr)
        cmd = None
        #cmd = self.decode_sdp(data)#scp_message.Command(data)
        if  cmd is None:
                print 'Message seems to be random. Echoing...\n\n\n'
                reply = "This is what vSpiNNaker received: " + data
                self.my_socket.sendto(str(cmd), addr)
        else:
            print 'Received a SDP message\n\n\n'
            reply = "vSpiNNaker decoded the following command: " + str(cmd)
            self.my_socket.sendto(str(cmd), addr)


    def decode_cmd(self, value):
        for k,v in scp_cmd.SCPCommand._value2member_map_.items():
            k1 = int()
            k2 = str()
            if isinstance(k, tuple):
                k1,k2 = k
            else:
                k1 = k
                k2 = ""
            if str(value).isdigit() and k1 == int(value):
                return v
        return None


    # def decode_scp(self,packet):
    #     try:
    #         ba = bytearray(packet)
    #         cmd_rc =bs[0:15].uint
    #         seq = bs[16:31].uint
    #         return self.decode(cmd_rc)
    #     except Exception as e:
    #         return None


    def decode_sdp(self,packet):
        try:
            bs = bytearray(packet)
            flags = int(bs[0])
            if flags == sdp_flg.SDPFlag.REPLY_NOT_EXPECTED.value:
                print 'No reply expected'
            print 'flags =', flags
            sdp_header = int(str(bs[0:8]), 16)
            print 'sdp_header =', sdp_header
            scp_body = bs[9:24]
            print 'scp_body =', scp_body
            cmd_rc = int(scp_body[0:1])
            print 'cmd_rc =', cmd_rc
            return self.decode_cmd(cmd_rc)
        except Exception as e:
            print e.message
            return None


    def close(self):
        self.my_socket.close()


if __name__ == "__main__":
    try:
        vs = VirtualSpiNNaker('localhost',17893)
        vs.rcv()
    except Exception as e:
        print e
    finally:
        print 'Closing the socket'
        try:
            vs.close()
            print 'Closed the socket'
        except Exception as exc:
            print 'Could not close the socket'
