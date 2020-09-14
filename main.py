import sounddevice as sd
import keyboard

from sampler import sampler
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

key_numbers = [*range(0,25)] # 25 keys
pedal = 25
shift = 26

GPIO.setwarnings(False) # Ignore warning for now, TODO: forget about revisiting this
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
for key in key_numbers:
    GPIO.setup(key, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means
GPIO.setup(pedal, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means
GPIO.setup(shift, GPIO.IN, pull_up_down=GPIO.PUD_UP) # TODO: figure out what this means


shift_count = 0 # keeps track of how many time shifting between key sets has been triggered
old_shift_button_state = False


sampler = sampler.Sampler()
sample_map = {0:"sampler/note.wav", 1:"sampler/note2.wav", 2: "sampler/note3.wav", 3: "sampler/note_R.wav"}
sampler.load(sample_map)
sampler.start()
    
while not keyboard.is_pressed('q'):
    pressed_map = {}
    for key in key_numbers:
        pressed_map[key] = GPIO.input(key) == GPIO.LOW
    pressed_keys = [key for key in key_numbers if pressed_map[key]]
    pedal_pressed = GPIO.input(pedal) == GPIO.LOW
    
    # on key up of shift button, increment shift count
    if (not (GPIO.input(shift) == GPIO.LOW) and old_shift_button_state):
        shift_count = shift_count + 1
    old_shift_button_state = GPIO.input(shift) == GPIO.LOW
    
    # TODO: Figure out if Mihir's library is stateful
    # TODO: Figure out if we need to do sound device setup for Mihir's library
    # mihirs_dope_ass_sound_library(pressed_keys, pedal_pressed, shift_count) # TODO: Import library, mod shift_count before passing in?
    # print(pressed_keys)
    sampler.update(pressed_keys)
    
    # print([0 if pressed_map[key] else 1 for key in key_numbers])
    # print(pressed_keys)
    # print(pedal_pressed)
    # print(shift_count)
sampler.close()



