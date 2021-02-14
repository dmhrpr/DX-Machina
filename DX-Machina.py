import mido
import pyaudio
import wave
from random import randint as r
import glob
from time import sleep
import subprocess
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import re



def setup_midi():
    all_midi_outputs = mido.get_output_names()
    if any("reface DX" in s for s in all_midi_outputs):
        port = mido.open_output("reface DX")
    else:
        print("Please connect your Reface DX and try again.")
        quit()



def init_patches():
    for patch in range(32):
        header = [67, 0, 127, 28, 0, 4, 5, 14, 15, 0, 94]

        com = [67, 0, 127, 28, 0, 42, 5, 48, 0, 0, r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), 0, 0, r(40, 88), r(0, 3), r(0, 127), r(40, 88), r(0, 11), r(0, 7), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(16, 112), r(16, 112), r(16, 112), r(16, 112), r(0, 7), r(0, 127), r(0, 127), r(0, 7), r(0, 127), r(0, 127), 0, 0, 0]

        op1 = [67, 0, 127, 28, 0, 32, 5, 49, 0, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(63, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        op2 = [67, 0, 127, 28, 0, 32, 5, 49, 1, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(0, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        op3 = [67, 0, 127, 28, 0, 32, 5, 49, 2, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(0, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        op4 = [67, 0, 127, 28, 0, 32, 5, 49, 3, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(0, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        footer = [67, 0, 127, 28, 0, 4, 5, 15, 15, 0, 93]

        voice_syx = [com, op1, op2, op3, op4]

        for syx in voice_syx:
            data = syx[6:]
            checksum = (sum(data)) % 128
            if checksum == 127:
                checksum = checksum
            elif checksum == 0:
                checksum = checksum
            else:   
                checksum = 128 - checksum
            syx.append(checksum)

        header = mido.Message("sysex", data=header)
        com = mido.Message("sysex", data=com)
        op1 = mido.Message("sysex", data = op1)
        op2 = mido.Message("sysex", data = op2)
        op3 = mido.Message("sysex", data = op3)
        op4 = mido.Message("sysex", data = op4)
        footer = mido.Message("sysex", data=footer)

        syx_file = [header, com, op1, op2, op3, op4, footer]

        mido.write_syx_file("patch-" + (str(patch)).zfill(2) + ".syx", syx_file)



def get_all_syx():
    all_syx = [s for s in glob.glob("*.syx") if s.startswith("patch")]
    for syx in all_syx:
        recorder(syx)



def recorder(filename):
    port = mido.open_output("reface DX")
    
    patch = mido.read_syx_file(filename)

    for msg in patch:
        port.send(msg)

    c3_note = mido.Message("note_on", note=60, velocity=100)
    c3_note_off = mido.Message("note_off", note=60)

    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second
    seconds = 3
    filename = filename

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True, input_device_index=2) 

    frames = []  # Initialize array to store frames

    port.send(c3_note)

# Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

# Stop and close the stream 
    stream.stop_stream()
    stream.close()
# Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

# Save the recorded data as a WAV file
    wf = wave.open(filename.split(".")[0] + ".wav", 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()    

    port.send(c3_note_off)
    sleep(1)



def mfcc(source_audio):
    source_output = subprocess.run(["aubio", "mfcc", source_audio], stdout=subprocess.PIPE).stdout.decode('utf-8')

    source_mfcc_values = []

    for value in source_output.split():
        source_mfcc_values.append(float(value))
        
    all_wav = [s for s in glob.glob("*.wav") if s.startswith("patch")]

    for wav in all_wav:          
        output = subprocess.run(["aubio", "mfcc", wav], stdout=subprocess.PIPE).stdout.decode("utf-8")
        mfcc_values = []
        for value in output.split():
            mfcc_values.append(float(value))

        similarity_score = []

        for data in mfcc_values:
            difference = abs(data - source_mfcc_values[(mfcc_values.index(data))])

            similarity_score.append(difference)

        if (sum(similarity_score)) / (len(similarity_score)) == 0:
            avg = 0.0
        else:   
            avg = round((sum(similarity_score)) / (len(similarity_score)), 2) 
   
        os.rename(wav.split(".")[0] + ".syx", (str(avg).replace(".", "")) + ".syx")
        os.rename(wav, (str(avg).replace(".", "")) + ".wav")

    best_wav()


def mutate():   
    prev_worst = sorted([s for s in glob.glob("*.syx") if s[0].isnumeric()])[16:]
    
    for i in prev_worst:
        os.remove(i)
     
    prev_iteration = sorted([s for s in glob.glob("*.syx") if s[0].isnumeric()])[:16]
    closest_matches = prev_iteration + prev_iteration
    
    patch_no = -1

    for match in closest_matches:
        patch_no = patch_no + 1
        prev_syx_file = mido.read_syx_file(match)[1:6]

        header = [67, 0, 127, 28, 0, 4, 5, 14, 15, 0, 94]
        com = [int(s) for s in re.findall(r'\b\d+\b', str(prev_syx_file[0])[12:-8])][:-1]
        op1 = [int(s) for s in re.findall(r'\b\d+\b', str(prev_syx_file[1])[12:-8])][:-1] 
        op2 = [int(s) for s in re.findall(r'\b\d+\b', str(prev_syx_file[2])[12:-8])][:-1] 
        op3 = [int(s) for s in re.findall(r'\b\d+\b', str(prev_syx_file[3])[12:-8])][:-1] 
        op4 = [int(s) for s in re.findall(r'\b\d+\b', str(prev_syx_file[4])[12:-8])][:-1] 
        footer = [67, 0, 127, 28, 0, 4, 5, 15, 15, 0, 93]       

        com_params = [24, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 43, 44]

        for param in com_params:
            p = com[param]
            if p >= 102:
                com[param] = (p - 50) + r(0, 50)
            elif p <= 25:
                com[param] = p + r(0, 50)
            else:
                com[param] = (p - 25) + r(0, 50)

        com[26] = r(0, 11)
        com[27] = r(0, 7)
        com[39] = r(0, 7)
        com[40] = r(0, 7)

        op_params = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 24, 27, 28, 29, 34]
        
        for param in op_params:
            p = op1[param]
            if p >= 102:
                op1[param] = (p - 50) + r(0, 50)
            elif p <= 25:
                op1[param] = p + r(0, 50)
            else:
                op1[param] = (p - 25) + r(0, 50)

            p = op2[param]
            if p >= 102:
                op2[param] = (p - 50) + r(0, 50)
            elif p <= 25:
                op2[param] = p + r(0, 50)
            else:
                op2[param] = (p - 25) + r(0, 50)

            p = op2[param]
            if p >= 102:
                op2[param] = (p - 50) + r(0, 50)
            elif p <= 25:
                op2[param] = p + r(0, 50)
            else:
                op2[param] = (p - 25) + r(0, 50)

            p = op1[param]
            if p >= 102:
                op1[param] = (p - 50) + r(0, 50)
            elif p <= 25:
                op1[param] = p + r(0, 50)
            else:
                op1[param] = (p - 25) + r(0, 50)

        op1[22] = r(0, 3)
        op1[23] = r(0, 3)
        op1[25] = r(0, 1)
        op1[26] = r(0, 1)
        op1[30] = r(0, 1)
        op1[31] = r(0, 1)
        op1[32] = r(0, 31)
        op1[33] = r(0, 99)

        op2[22] = r(0, 3)
        op2[23] = r(0, 3)
        op2[25] = r(0, 1)
        op2[26] = r(0, 1)
        op2[30] = r(0, 1)
        op2[31] = r(0, 1)
        op2[32] = r(0, 31)
        op2[33] = r(0, 99)

        op3[22] = r(0, 3)
        op3[23] = r(0, 3)
        op3[25] = r(0, 1)
        op3[26] = r(0, 1)
        op3[30] = r(0, 1)
        op3[31] = r(0, 1)
        op3[32] = r(0, 31)
        op3[33] = r(0, 99)

        op4[22] = r(0, 3)
        op4[23] = r(0, 3)
        op4[25] = r(0, 1)
        op4[26] = r(0, 1)
        op4[30] = r(0, 1)
        op4[31] = r(0, 1)
        op4[32] = r(0, 31)
        op4[33] = r(0, 99)
 
        voice_syx = [com, op1, op2, op3, op4]

        for syx in voice_syx:
            data = syx[6:]
            checksum = (sum(data)) % 128
            if checksum == 127:
                checksum = checksum
            elif checksum == 0:
                checksum = checksum
            else:   
                checksum = 128 - checksum
            syx.append(checksum)

        header = mido.Message("sysex", data = header)
        com = mido.Message("sysex", data = com)
        op1 = mido.Message("sysex", data = op1)
        op2 = mido.Message("sysex", data = op2)
        op3 = mido.Message("sysex", data = op3)
        op4 = mido.Message("sysex", data = op4)
        footer = mido.Message("sysex", data = footer)

        syx_file = [header, com, op1, op2, op3, op4, footer]
            
        mido.write_syx_file("patch-" + str(patch_no).zfill(2) + ".syx", syx_file)

    for i in prev_iteration:
        os.rename(i, "Previous_Iterations/" + i)



def best_wav():        
    prev_iteration = sorted([s for s in glob.glob("*.wav") if s[0].isnumeric()])[:16]
    for wav in prev_iteration:
        os.rename(wav, "Prev_Wav/" + wav)
    rest = glob.glob("*.wav")
    for r in rest:
        os.remove(r)


os.mkdir("Previous_Iterations")
os.mkdir("Prev_Wav")
setup_midi()
Tk().withdraw()
source_audio = askopenfilename()
init_patches()
get_all_syx()
mfcc(source_audio)
mutate()

while True:
    get_all_syx()
    mfcc(source_audio)
    mutate()
