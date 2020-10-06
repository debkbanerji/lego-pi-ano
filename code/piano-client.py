import socket
import sys
import numpy as np

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)

print('Writing piano information to {}, port {}'.format(server_address[0],server_address[1]))

while(True):

    # TODO: Read in from raspberry pi GPIO
    message = np.array([0,1,2,3,4], dtype='uintc')
    sock.sendto(message.tobytes(), server_address)
