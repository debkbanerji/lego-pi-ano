# Warning: this is an incomplete version of the code, but can probably be completed using the code from piano-server.py

import sounddevice as sd
import keyboard

from sampler import sampler
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

key_offset = 2 # start from GPIO 2
key_numbers = [*range(0, 25)] # 25 keys
# pedal = 25
# shift = 26

GPIO.setwarnings(False) # Ignore warning for now, TODO: forget about revisiting this
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
for key in key_numbers:
    GPIO.setup(key, GPIO.IN, pull_up_down=GPIO.PUD_UP)


shift_count = 0 # keeps track of how many time shifting between key sets has been triggered
old_shift_button_state = False


sampler = sampler.Sampler()
notes = ["sampler/samples/legopiano1/"+str(i).zfill(2)+".wav" for i in key_numbers]#, "sampler/note2.wav", "sampler/note3.wav"]
sample_map = {}
# for i in range(len(key_numbers)):
    # sample_map[i] = notes[i]
# sample_map = {0:"sampler/note.wav", 1:"sampler/note2.wav", 2: "sampler/note3.wav", 3: "sampler/note_R.wav"}
sampler.load(sample_map)
sampler.start()

while not keyboard.is_pressed('q'):
    pressed_map = {}
    for key in key_numbers:
        pressed_map[key] = GPIO.input(key) != GPIO.LOW
    pressed_keys = [key for key in key_numbers if pressed_map[key]]
    print(pressed_keys)
    pedal_pressed = GPIO.input(pedal) == GPIO.LOW

    # TODO: port over code from piano-server.py
sampler.close()
