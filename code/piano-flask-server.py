from flask import Flask
from queue import Queue
import json
import numpy as np
import threading
import time
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

MAX_BUFFER_SIZE = 50 # add a little memory for if a key was pressed - tweak this if things seem off
BUFFER_MAX_TIME_NS  = 500 * 1000 * 1000 # 0.5 seconds

buffer = Queue(maxsize=MAX_BUFFER_SIZE)
buffer_timestamps = Queue(maxsize=MAX_BUFFER_SIZE)

NUM_KEYS = 26  # 25 keys + pedal
key_numbers = [*range(0, NUM_KEYS)]
pressed_keys = np.zeros(NUM_KEYS)

key_offset = 2 # start from GPIO 2

GPIO.setwarnings(False) # Ignore warning for now, TODO: forget about revisiting this
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
for key in key_numbers:
    GPIO.setup(key + key_offset, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means


port = 8080
app = Flask(__name__,
            static_url_path='',
            static_folder='static')

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/keys') # Test endpoint
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

            input_time = time.time_ns()
            if buffer.full():
                buffer.get()
                buffer_timestamps.get()

            while not buffer.empty() and input_time - buffer_timestamps.queue[0] > BUFFER_MAX_TIME_NS:
                buffer.get()
                buffer_timestamps.get()

            if buffer.empty() or not np.array_equal(buffer.queue[-1], pressed_keys):
                buffer.put(pressed_keys)
                buffer_timestamps.put(input_time)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False, threaded=True))
    hardware_thread  = Pin_Listener_Thread("hardware_thread")

    flask_thread.start()
    hardware_thread.start()

    flask_thread.join()
    hardware_thread.join()
