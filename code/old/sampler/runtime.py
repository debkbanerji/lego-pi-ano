from sampler import Sampler
import cython_helloworld as hw
import time
import numpy as np

sampler = None
sample_map = None

def setup():
    global sampler, sample_map
    sampler = Sampler(sample_rate=48000, record_enabled=True, disable_output=True)
    # sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav"}
    sample_map = {"a":"01.wav", "s":"02.wav", "d": "03.wav", "f": "04.wav", "g": "05.wav", "h": "06.wav", "j": "07.wav", "k": "08.wav", "l": "09.wav", ":": "10.wav", "'":"11.wav", "w":"12.wav", "e":"13.wav", "r":"14.wav", "t":"15.wav", "y":"16.wav", "u":"17.wav", "i":"18.wav", "o":"19.wav", "p":"20.wav", "[": "21.wav", "]":"22.wav"}
    sampler.load(sample_map, "samples/legopiano1/")
    sampler.start()

def close():
    sampler.close()

def time_block(repetitions=1):
    # keys_pressed = ["a", "s", "d", "f"]
    keys_pressed = list(sample_map.keys())
    start = time.time_ns()
    for i in range(repetitions):
        sampler.update(keys_pressed)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_block_opt(repetitions=1):
    # keys_pressed = ["a", "s", "d", "f"]
    keys_pressed = list(sample_map.keys())
    start = time.time_ns()
    for i in range(repetitions):
        sampler.update_optimized(keys_pressed)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_block_opt_v2(repetitions=1):
    # keys_pressed = ["a", "s", "d", "f"]
    # keys_pressed = list(sample_map.keys())
    sampler.disable_output = False
    keys = []
    for i in range(len(sample_map.keys())):
        keys.append(1)
    keys_arr = np.array(keys, dtype=np.int16)
    start = time.time_ns()
    for i in range(repetitions):
        sampler.update_optimized_v2(keys_arr)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_arr_fill(repetitions=1):
    start = time.time_ns()
    for i in range(repetitions):
        hw.set_array(20000)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def time_arr_fill_opt(repetitions=1):
    start = time.time_ns()
    for i in range(repetitions):
        hw.set_array_optimized(20000)
    end = time.time_ns()
    print(f"Time: {end-start} ns, {(end-start) / (10 ** 9)} sec")

def keyToAsciiBuffer(char_arr) -> int:
    result: int
    result = 0
    if len(char_arr) > 4:
        raise Exception("char array must not exceed 4")
    #input unicode
    #output int
    for i in range(len(char_arr)):
        result = (result << 8) | ord(char_arr[i])
    return result

def asciiToKey(ascii: int):
    result = []
    for i in range(4):
        chunk = ascii & 255
        ch = chr(chunk)
        result.insert(0, ch)
        ascii = ascii >> 8
    return result
def test_keyToInt():
    # print(sampler.keyToInt(bytearray('a', encoding="utf-8")))
    # print(keyToInt(bytearray('a', encoding="utf-8")))
    print(keyToAsciiBuffer(np.array(list("k4"))))
    print(asciiToKey(27444))

if __name__ == "__main__":
    setup()
    # test_keyToInt()
    # time_block(750)
    # time.sleep(6)
    # time_block_opt(750)
    time_block_opt_v2(1500)
    # time_arr_fill(1000)
    # time_arr_fill_opt(1000)

# Target benchmarks for 48khz sample rate
# current time for 64 * 2 sample block: 96858200 ns = 0.0968582
# target for 48khz sample rate: 
#   48000 samples per sec / 64 samples = 750 blocks per second
#   Avg time for blocks = 1333333.33 ns per block = 0.00133333333 second per block
