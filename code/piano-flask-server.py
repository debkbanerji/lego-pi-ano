from flask import Flask
from queue import Queue
import json
import numpy as np
import threading
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

BUFFER_SIZE = 300 # add a little memory for if a key was pressed - tweak this if things seem off
buffer = Queue(maxsize=BUFFER_SIZE)

NUM_KEYS = 26  # 25 keys + pedal
key_numbers = [*range(0, NUM_KEYS)]
pressed_keys = np.zeros(NUM_KEYS)

key_offset = 2 # start from GPIO 2

GPIO.setwarnings(False) # Ignore warning for now, TODO: forget about revisiting this
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
for key in key_numbers:
    GPIO.setup(key + key_offset, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means


host_name = None
port = 8080
app = Flask(__name__)
@app.route('/test') # Test endpoint
def test():
    return 'Hello from Pi-ano server'

@app.route('/') # Test endpoint
def main():
    buffer_array = np.array(buffer.queue)
    sum_array = buffer_array.sum(axis=0)
    result_array = np.where(sum_array > 0, 1, 0)
    return json.dumps(result_array.tolist())

class Pin_Listener_Thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global pressed_keys
        while True:
            pressed_map = {}
            for key in key_numbers:
                pressed_map[key] = GPIO.input(key + key_offset) == GPIO.LOW
            pressed_keys = np.array([1 if pressed_map[key] else 0 for key in key_numbers], dtype=np.uintc)

            if buffer.full():
                buffer.get()
            buffer.put(pressed_keys)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False))
    hardware_thread  = Pin_Listener_Thread("hardware_thread")

    flask_thread.start()
    hardware_thread.start()

    flask_thread.join()
    hardware_thread.join()
