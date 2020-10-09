import socket
import sys
import time
import numpy as np
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

key_offset = 2 # start from GPIO 2
key_numbers = [*range(0, 25)] # 25 keys

GPIO.setwarnings(False) # Ignore warning for now, TODO: forget about revisiting this
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
for key in key_numbers:
    GPIO.setup(key + key_offset, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (SERVER_LAN_ADDRESS_STRING_HERE, 11111)

print('Writing piano information to {}, port {}'.format(server_address[0],server_address[1]))

current_buffer = np.zeros(len(key_numbers))
buffer_reset_index = 0
buffer_size = 300

while(True):

    pressed_map = {}
    for key in key_numbers:
        pressed_map[key] = GPIO.input(key + key_offset) != GPIO.LOW
    pressed_keys = np.array([1 if pressed_map[key] else 0 for key in key_numbers], dtype='short')
    current_buffer = np.vstack([current_buffer, pressed_keys])
    
    buffer_reset_index = (buffer_reset_index + 1) % buffer_size
    if (buffer_reset_index == 0):
        buffer_sum = current_buffer.sum(axis=0)
        smoothed_pressed_keys = np.array([1 if i > buffer_size / 2 else 0 for i in buffer_sum], dtype='short')
        # print(smoothed_pressed_keys)

        sock.sendto(smoothed_pressed_keys.tobytes(), server_address)
        
        # reset buffer
        current_buffer = np.zeros(len(key_numbers))
