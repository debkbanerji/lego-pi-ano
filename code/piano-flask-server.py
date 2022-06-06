from flask import Flask
import json
import numpy as np
import threading
# import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

NUM_KEYS = 26  # 25 keys + pedal
key_numbers = [*range(0, NUM_KEYS)]
pressed_keys = np.zeros(NUM_KEYS)

key_offset = 2 # start from GPIO 2

# GPIO.setwarnings(False) # Ignore warning for now, TODO: forget about revisiting this
# GPIO.setmode(GPIO.BCM) # Use physical pin numbering
# for key in key_numbers:
#     GPIO.setup(key + key_offset, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means


host_name = None
port = 8080
app = Flask(__name__)
@app.route('/test') # Test endpoint
def test():
    return 'Hello from Pi-ano server'

@app.route('/') # Test endpoint
def main():
    return json.dumps(pressed_keys.tolist())

class Pin_Listener_Thread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        global pressed_keys
        while True:
            pressed_keys = np.random.randint(2, size=NUM_KEYS) # TODO: Replace with hardware stuff (with max over time window logic)

            # TODO: Buffer maxing logic - add a little memory for if a key was pressed
            # pressed_map = {}
            # for key in key_numbers:
            #     pressed_map[key] = GPIO.input(key + key_offset) != GPIO.LOW
            # pressed_keys = np.array([1 if pressed_map[key] else 0 for key in key_numbers], dtype=np.uintc)

            print(pressed_keys)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False))
    hardware_thread  = Pin_Listener_Thread("hardware_thread")

    flask_thread.start()
    hardware_thread.start()

    flask_thread.join()
    hardware_thread.join()
