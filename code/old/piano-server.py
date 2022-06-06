import socket
import sys
import numpy as np
from sampler import sampler

NUM_KEYS = 26
key_numbers = [*range(1, NUM_KEYS + 1)]

sampler = sampler.Sampler()
notes = ["sampler/samples/legopiano1/"+str(i).zfill(2)+".wav" for i in key_numbers]#, "sampler/note2.wav", "sampler/note3.wav"]
sample_map = {}
for i in range(len(key_numbers)):
    sample_map[str(i)] = notes[i]
sampler.load(sample_map)
sampler.start()

# set up UDP server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)

server_address = (SERVER_LAN_ADDRESS_STRING_HERE, 11111)
print('Listening on {}, port {}'.format(server_address[0], server_address[1]))
sock.bind(server_address)

old_pressed_keys = None
pressed_keys = np.zeros(25, dtype=np.uintc)
try:
    while True:
        try:
            data, _address = sock.recvfrom(1024) # 1024 is arbitrarily chosen as packet size? - idk if that's what it is, but it works
            # print(sys.getsizeof(data))
            pressed_keys = np.frombuffer(data, dtype=np.uintc)[:NUM_KEYS]
            # print(pressed_keys)
            if old_pressed_keys is None or not np.array_equal(old_pressed_keys, pressed_keys):
                print(pressed_keys)
            sampler.update_optimized_v2(pressed_keys.copy())
            old_pressed_keys = pressed_keys
        except Exception as e:
            sampler.update_optimized_v2(pressed_keys.copy())
except KeyboardInterrupt:
    sampler.close()
