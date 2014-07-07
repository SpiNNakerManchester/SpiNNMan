__author__ = 'Petrut'
import socket

host = 'localhost'
port = 17893
print "Booting vSpiNNaker"
my_socket = socket.socket(type= socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.bind((host,port))
#my_socket.listen(1)
print "Everything set up. Listening for connection."
while True:
    data, addr = my_socket.recvfrom(port)
    print 'Contacted by ', addr
    print 'Sending response back'
    reply = "This is what vSpiNNaker received: " + data
    my_socket.sendto(reply, addr)

my_socket.close()