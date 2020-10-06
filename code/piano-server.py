# TODO: write
import socket
import sys
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
print('Listing on {}, port {}'.format(server_address[0], server_address[1]))
sock.bind(server_address)

while True:

    data, address = sock.recvfrom(1024) # 1024 is arbitrarily chosen as packet size? - idk if that's what it is, but it works
    pressed_keys = np.frombuffer(data, dtype='uintc')

    # TODO: send pressed keys to sampler

    print('received {} bytes from {}'.format(len(data), address))
    print(pressed_keys)
