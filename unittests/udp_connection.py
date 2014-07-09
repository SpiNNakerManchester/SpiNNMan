__author__ = 'Petrut'
import spinnman.connections.udp_connection as udp_conn

import socket   #for sockets
import sys  #for exit


# create dgram udp socket

class UDPConnection(object):
    def __init__(self, host, port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()

        self.host = host
        self.port = port


    def send_udp_message(self, msg):
        try :
            self.s.sendto(msg, (self.host, self.port))

            return self.receive_message()


        except socket.error, msg:
            return 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

    def receive_message(self):
        d = self.s.recvfrom(1024)
        reply, addr = d

        return reply
    def send_scp_message(self,msg):
        try :
            self.s.sendto(msg, (self.host, self.port))

            return self.receive_message()

        except socket.error, msg:
            return 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]


    def send_sdp_message(self,msg):
        try :
            self.s.sendto(msg, (self.host, self.port))

            return self.receive_message()

        except socket.error, msg:
            return 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]


    def sniff_socket(self,socket):
        d = socket.recvfrom(1024)
        reply, addr = d
        return reply

    def close(self):
        try:
            self.s.close()
        except Exception as e:
            return "Could not close the socket -> ", e.message

if __name__ == "__main__":
    conn = UDPConnection("localhost",17893)
    while True:
        msg = raw_input('Enter message to send : ')
        print conn.send_udp_message(msg)
