import wave
import itertools
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import sounddevice as sd
cimport cython

cdef class Sampler:
    cdef public object recording
    cdef public object record_enabled
    cdef public object samples
    cdef public object pos
    cdef public object chunk_size
    cdef public object dtype
    cdef public object stream
    cdef public object channels
    cdef public object output_buffer

    cdef public object sample_arr
    cdef public object key_arr

    cdef public object disable_output

    # C data types for optimized playback
    cdef short[:] sample_view                       # sample data... all samples in one contiguous block
    cdef unsigned int[:, :] sample_start_end_view   # Where each file starts/end in memory. index = file, [sample start, sample end]
    cdef unsigned int[:] key_view                   # key activation data
    cdef short[:] output_buffer_view                # output buffer
    cdef unsigned int[:] pos_view                   # sample position

    def keyToAsciiBuffer(self, char_arr) -> int:
        result: int
        result = 0
        if len(char_arr) > 4:
            raise Exception("char array must not exceed 4")
        #input unicode
        #output int
        for i in range(len(char_arr)):
            result = (result << 8) | ord(char_arr[i])
        return result

    def asciiToKey(self, ascii: int):
        result = []
        for i in range(4):
            chunk = ascii & 255
            ch = chr(chunk)
            result.insert(0, ch)
            ascii = ascii >> 8
        return result
    def __init__(self, record_enabled=False, sample_rate=44100, disable_output=False):
        self.recording = [] # Use for debug recording mode
        self.record_enabled = record_enabled # Used for debugging purposes only.
        self.samples = {} # key: String note name, value: loaded sample (numpy array)
        self.pos = {} # key: String note name, value integer indicating current playback position
        self.chunk_size = 64 # number of samples to process/stream at once
        self.dtype = np.int16
        self.stream = None
        self.channels = 2
        self.output_buffer = None # numpy array containing output samples to be streamed. size = self.channels x self.chunk_size
    
        self.sample_arr = None #Numpy arrays
        self.key_arr = None

        self.disable_output = disable_output

        # sd default
        sd.default.samplerate = sample_rate
        sd.default.channels = 2
        sd.default.dtype = 'int16'

    @cython.wraparound(False)
    def visualize(self, recording):
        recording_L = recording[::2]
        recording_R = recording[1::2]
        figs, axs = plt.subplots(2, sharex=True, sharey=True)
        figs.suptitle("Recording")
        axs[0].plot(recording_L)
        axs[1].plot(recording_R)
        plt.show()
        
    cpdef load(self, path_map, root_dir:str = "", gain=1.0):
        """
            path_map (Python Dict)
                key: String keyname
                value: String path_to_wav_file
                example: {"a":"c1.wav", ...}
        """
        # C data initializing
        cdef short[:] audio_arr_view
        cdef float sample
        cdef float fgain = <float> gain
        cdef int i
        cdef short[:] np_data_view
        cdef unsigned int pos = 0
        files = []
        np_files = np.array(files, dtype=self.dtype)
        start_end = []
        keys: List[int] = []
        for key in path_map:
            # read wavefile by loading into numpy array
            wf = wave.open(root_dir + path_map[key], 'rb')
            # np_data_view = np.fromfile(root_dir + path_map[key], dtype=self.dtype)
            nframes = wf.getnframes()
            audio = wf.readframes(nframes)
            samplewidth = wf.getsampwidth()
            nsamples = nframes * 1
            channels = wf.getnchannels()
            np_data_view = np.frombuffer(audio, dtype=self.dtype).copy()
            # reduce volume
            audio_arr = np.zeros(nsamples, dtype=self.dtype)
            audio_arr_view = audio_arr
            for i in range(audio_arr_view.shape[0]):
                sample = <float> np_data_view[i]
                sample = (sample * fgain) + .5
                audio_arr_view[i] = <short> sample
            print("ndim:", audio_arr.ndim, "shape:", audio_arr.shape)
            print("loaded", path_map[key], "nframes =", nframes, "nsamples =", nsamples, "samplewidth (in bytes) =", samplewidth, "channels =", channels)
            self.samples[key] = audio_arr

            files.append(audio_arr)
            np.concatenate((np_files, audio_arr))
            keys.append(self.keyToAsciiBuffer(list(key)))
            start_end.append([pos, pos + audio_arr_view.shape[0]])
            pos = pos + audio_arr_view.shape[0]
            # self.visualize(audio_arr)

        # intialize sample playback positions
        self.pos = self.samples.copy()
        for key in self.pos:
            self.pos[key] = 0
        self.pos_view = np.zeros(len(keys), dtype=np.uint)

        # initialize output buffer
        self.output_buffer =  np.zeros(self.channels * self.chunk_size, dtype=self.dtype)
        self.output_buffer_view = self.output_buffer
        # print("output_buffer initialized:", self.output_buffer)
        # print("output_buffer dtype:", self.output_buffer.dtype)

        # initialize sample array
        self.sample_arr = np.array(list(itertools.chain.from_iterable(files)), dtype=self.dtype)
        # self.sample_arr = np_files
        self.sample_view = self.sample_arr
        # print("sample_arr:", self.sample_arr)
        # print("sample_view: ", self.sample_view)
        print("start_end:", start_end)
        self.sample_start_end_view = np.array(start_end, dtype=np.uint)
        print("sample_start_end:", self.sample_start_end_view[:])
        # initialize key array
        self.key_arr = np.array(keys, dtype=np.uint)
        self.key_view = self.key_arr
        # print("key_arr:", self.key_arr)
        # print("key_view:", self.key_view)

        # self.visualize(self.sample_view)
    
    def generate_key_press_array(self):
        return np.zeros(len(self.key_arr), dtype=np.int16)

    def update(self, notes_pressed):
        """
            Sends samples to output stream based on incoming events
            Parameters:
                notes_pressed: List of notes pressed. Notes are strings that must match the keys of self.samples exactly.
        """
        sound_playing = False
        # Zero the output buffer
        self.output_buffer.fill(0)
        for note in self.samples: #NOTE: can decrease iterations by only going through notes_pressed list. Currently this implementation will detect when a "keyup" event happens...in this case, the sample position will be set back to 0
            if note in notes_pressed:
                sound_playing = True
                sample = self.samples[note]
                iter = np.nditer(self.output_buffer, flags=['f_index'])
                for s in iter:
                    sample_index = iter.index + self.pos[note]
                    if sample_index < sample.size:
                        self.output_buffer[iter.index] = s + sample[sample_index]
                self.pos[note] = self.pos[note] + self.output_buffer.size
            else:
                self.pos[note] = 0
        # DEBUGGING-------
        # print(self.output_buffer)
        # print(self.samples[note][:self.chunk_size * 2])
        # print("buffer dtype:", self.output_buffer.dtype, "sample dtype:", self.samples[note].dtype)
        # exit()
        # self.stream.write(self.samples[note])
        #-----------------
        if sound_playing:
            if not self.disable_output:
                self.stream.write(self.output_buffer)
            if self.record_enabled:
                self.recording.append(np.array(self.output_buffer, dtype=self.dtype))
    
    @cython.wraparound(False)
    cpdef update_optimized(self, list notes_pressed):
        cdef bint sound_playing = False
        cdef int i
        cdef int sample_index
        cdef short[:] sample
        # Zero the output buffer
        for i in range(self.output_buffer_view.shape[0]):
            self.output_buffer_view[i] = 0
        for note in self.samples:
            if note in notes_pressed:
                sound_playing = True
                sample = self.samples[note]
                for i in range(self.output_buffer_view.shape[0]):
                    sample_index = i + <int> self.pos[note]
                    if sample_index < sample.shape[0]:
                        self.output_buffer_view[i] = self.output_buffer_view[i] + sample[sample_index]
                self.pos[note] = self.pos[note] + self.output_buffer_view.shape[0]
            else:
                self.pos[note] = 0
        if sound_playing:
            if not self.disable_output:
                self.stream.write(self.output_buffer_view)
            if self.record_enabled:
                self.recording.append(np.array(self.output_buffer, dtype=self.dtype))

    
    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef update_optimized_v2(self, short[:] keys_arr):
        cdef bint sound_playing = False
        cdef unsigned int i
        cdef unsigned int p
        cdef unsigned int sample_index
        cdef short[:] sample
        # """
        # Zero the output buffer
        for i in range(self.output_buffer_view.shape[0]):
            self.output_buffer_view[i] = 0
        # for every sound file
        for p in range(self.sample_start_end_view.shape[0]):
            if keys_arr[p] == 1 and self.pos_view[p] < self.pos_view[p] + self.sample_start_end_view[p][1]: # if key down and sample isn't at end
                sound_playing = True
                for i in range(self.output_buffer_view.shape[0]):
                    sample_index = i + self.sample_start_end_view[p][0] + self.pos_view[p]
                    if sample_index < self.sample_start_end_view[p][1]:
                        self.output_buffer_view[i] = self.output_buffer_view[i] + self.sample_view[sample_index] 

                '''
                sample = self.sample_view[p]
                for i in range(self.output_buffer_view.shape[0]):
                    sample_index = i + self.pos_view[p]
                    if sample_index < sample.shape[0]:
                        self.output_buffer_view[i] = self.output_buffer_view[i] + sample[sample_index]
                '''
                self.pos_view[p] = self.pos_view[p] + self.output_buffer_view.shape[0]
            else:
                self.pos_view[p] = 0
        if sound_playing:
            if not self.disable_output:
                self.stream.write(self.output_buffer_view)
            if self.record_enabled:
                self.recording.append(np.array(self.output_buffer, dtype=self.dtype))
        # """
    def start(self):
        print(sd.query_devices())
        self.stream = sd.OutputStream()
        self.stream.start()
        print("Sample rate:", sd.default.samplerate, "channels:", sd.default.channels, "chunk size:", self.chunk_size, "debug recording mode:", self.record_enabled, "disable output:", self.disable_output)
        print("Sampler started...")
    def close(self):
        if self.record_enabled:
            recording = [item for sublist in self.recording for item in sublist]
            self.visualize(recording)
            print("Playing recording...")
            self.stream.write(recording)
        self.stream.stop()
        print("Sampler stopped.")