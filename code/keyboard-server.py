import socket
import sys
import numpy as np
from pykeyboard import PyKeyboard


k = PyKeyboard()

NUM_KEYS = 26
key_numbers = [*range(1, NUM_KEYS + 1)]
# set up UDP server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)

server_address = (SERVER_LAN_ADDRESS_STRING_HERE, 11111)
print('Listening on {}, port {}'.format(server_address[0], server_address[1]))
sock.bind(server_address)

key_bindings = { # maps piano key index to server computer key
    5: 'a',
    6: 'w',
    7: 's',
    9: 'd'
}


old_pressed_keys = None
pressed_keys = np.zeros(NUM_KEYS, dtype=np.uintc)
try:
    while True:
        try:
            data, _address = sock.recvfrom(1024) # 1024 is arbitrarily chosen as packet size? - idk if that's what it is, but it works
            pressed_keys = np.frombuffer(data, dtype=np.uintc)[:NUM_KEYS].astype(int)
            if old_pressed_keys is not None and not np.array_equal(old_pressed_keys, pressed_keys):
                key_diff = np.subtract(pressed_keys, old_pressed_keys)
                for i, j in enumerate(key_diff):
                    if (j > 0) and i in key_bindings:
                        k.press_key(key_bindings[i])
                        # print('pressing ' + key_bindings[i])
                    elif (j < 0) and i in key_bindings:
                        k.release_key(key_bindings[i])
                        # print('releasing ' + key_bindings[i])
            old_pressed_keys = pressed_keys
        except Exception as e:
            pass
except KeyboardInterrupt:
    for key in key_bindings.values():
        k.release_key(key)
