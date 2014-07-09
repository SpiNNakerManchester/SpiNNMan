__author__ = 'Petrut'
import socket
from spinn_machine import processor as proc , link as link , sdram as sdram, router as router, chip as chip
import spinn_machine.exceptions as exc
import spinn_machine.machine as machine
import logging
import time
import spinnman.messages.scp_message as scp_message
import bitstring as bitstring

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
        cmd = self.decode(data)#scp_message.Command(data)
        if  cmd is None:
            print 'Not a command number'
            print '|-Checking if it a stand-alone SCP message'
            cmd = self.decode_scp(data)
            if cmd is None:
                print 'Not a stand-alone SCP message'
                print ' |-Checking if it is wrapped in an SDP message'
                cmd = self.decode_sdp(data)
                if cmd is None:
                    print 'Message seems to be random. Echoing...\n\n\n'
                    reply = "This is what vSpiNNaker received: " + data
                    self.my_socket.sendto(reply, addr)
                else:
                    print 'Received a SDP message\n\n\n'
                    reply = "vSpiNNaker decoded the following command: " + str(cmd)
                    self.my_socket.sendto(reply, addr)
            else:
                print 'Received stand-alone SCP message\n\n\n'
                reply = "vSpiNNaker decoded the following command: " + str(cmd)
                self.my_socket.sendto(reply, addr)
        else:
            print 'Received special command ', cmd,  '\n\n\n'
            reply = "vSpiNNaker decoded the following command: " + str(cmd)
            self.my_socket.sendto(reply, addr)

    def decode(self, value):
        for k,v in scp_message.Command._value2member_map_.items():
            k1 = int()
            k2 = str()
            if isinstance(k, tuple):
                k1,k2 = k
            else:
                k1 = k
                k2 = ""
            if value.isdigit() and k1 == int(value):
                return v
        return None


    def decode_scp(self,packet):
        try:
            bs = bitstring.BitArray(packet)
            cmd_rc =bs[0:15].uint
            seq = bs[16:31].uint
            return self.decode(cmd_rc)
        except Exception as e:
            return None


    def decode_sdp(self,packet):
        try:
            bs = bitstring.BitArray(packet)
            flag = bs[0:63].uint
            cmd_rc =bs[64:71].uint
            dest_port=bs[72:95].uint
            #dest_cpu = bs[]
            return self.decode(cmd_rc)
        except Exception as e:
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
