import keyboard
from sampler import Sampler
from keylistener import KeyListener

def start():
    sampler = Sampler(sample_rate=48000, record_enabled=False)
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav", "g": "05.wav", "h": "06.wav", "j": "07.wav", "k": "08.wav", "l": "09.wav", ":": "10.wav", "'":"11.wav", "w":"12.wav", "e":"13.wav", "r":"14.wav", "t":"15.wav", "y":"16.wav", "u":"17.wav", "i":"18.wav", "o":"19.wav", "p":"20.wav", "[": "21.wav", "]":"22.wav"}
    # sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav"}
    sampler.load(sample_map, "samples/legopiano1/")
    sampler.start()
    while not keyboard.is_pressed('q'):
        keys_pressed = []
        for key in sample_map:
            if keyboard.is_pressed(key):
                keys_pressed.append(key)
        # sampler.update(keys_pressed)
        sampler.update_optimized(keys_pressed)
    sampler.close()

def start_v2():
    sampler = Sampler(sample_rate=48000, record_enabled=False)
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav", "g": "05.wav", "h": "06.wav", "j": "07.wav", "k": "08.wav", "l": "09.wav", ":": "10.wav", "'":"11.wav", "w":"12.wav", "e":"13.wav", "r":"14.wav", "t":"15.wav", "y":"16.wav", "u":"17.wav", "i":"18.wav", "o":"19.wav", "p":"20.wav", "[": "21.wav", "]":"22.wav"}
    # sample_map = {"a":"legopiano1/01.wav", "s":"legopiano1/02.wav", "d": "legopiano1/03.wav", "f": "legopiano1/04.wav", "g": "note_R.wav", "h": "fork2.wav"}
    # sampler.load(sample_map, "samples/")
    sampler.load(sample_map, "samples/legopiano1/")
    sampler.start()
    listener = KeyListener(sampler)
    listener.start_listening()
    sampler.close()

if __name__ == "__main__":
    start_v2()