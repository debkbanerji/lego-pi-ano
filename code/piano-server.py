import socket
import sys
import numpy as np
from sampler import sampler

key_offset = 2 # start from GPIO 2 - we f***ed up earlier when using GPIo 1 and 2
key_numbers = [*range(1,25)] # 25 keys

sampler = sampler.Sampler()
notes = ["sampler/samples/legopiano1/"+str(i).zfill(2)+".wav" for i in key_numbers]#, "sampler/note2.wav", "sampler/note3.wav"]
sample_map = {}
for i in range(len(key_numbers)):
    sample_map[str(i)] = notes[i]
sampler.load(sample_map)
sampler.start()

# set up UDP server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
print('Listing on {}, port {}'.format(server_address[0], server_address[1]))
sock.bind(server_address)

while True:

    data, address = sock.recvfrom(1024) # 1024 is arbitrarily chosen as packet size? - idk if that's what it is, but it works
    pressed_keys = np.frombuffer(data, dtype='short')

    sampler.update_optimized_v2(pressed_keys.copy())