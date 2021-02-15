import contextlib
import glob
import math
import os
import random
import re
import subprocess
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import wave

import mido
import pyaudio

# Connect your audio interface and Reface DX by USB
# Ensure you also have Aubio and python-rtmidi installed in your virtual environment


r = random.randint
sleep = time.sleep
msg = mido.Message


def main():
    audio_input = CHOOSE_INPUT_DEVICE()
    port = SETUP_MIDI()
    print('\nChoose the audio sample you want to mimic.\n')
    sleep(1)
    Tk().withdraw()
    audio_file = askopenfilename()
    duration = GET_AUDIO_FILE_LENGTH(audio_file)
    audio_file_data = ANALYSE_AUDIO_FILE(audio_file)
    os.mkdir(audio_file.split('.')[0])
    os.chdir(audio_file.split('.')[0])
    INIT_PATCHES()
    RECORD_PATCHES(port, duration, audio_input)
    MFCC(audio_file_data)
    gen = 0
    MUTATE(gen)

    while True():
        gen = gen + 1
        gen_name = str(gen).zfill(4)
        print(f'Start of Generation {gen_name}.\n')
        RECORD_PATCHES(port, duration, audio_input)
        MFCC(audio_file_data)
        MUTATE(gen)

        
def CHOOSE_INPUT_DEVICE():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device ID", i, "-",
                  p.get_device_info_by_host_api_device_index(0, i).get('name'))

    audio_input = int(input('Enter the ID number of the Input Device you want to use. '))

    return audio_input


def SETUP_MIDI():
    try:
        port = mido.open_output('reface DX')
        return port
    except:
        print('Please connect your Reface DX and try again.')
        quit()


def GET_AUDIO_FILE_LENGTH(audio_file):
    with contextlib.closing(wave.open(audio_file, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)

    return duration


def ANALYSE_AUDIO_FILE(audio_file):
    analysis = subprocess.run(['aubio', 'mfcc', audio_file],
                              stdout=subprocess.PIPE).stdout.decode('utf-8').split()

    audio_file_data = []
    for x in analysis:
        audio_file_data.append(float(x))

    return audio_file_data


def INIT_PATCHES():
    for x in range(32):
        header = [67, 0, 127, 28, 0, 4, 5, 14, 15, 0, 94]

        com = [67, 0, 127, 28, 0, 42, 5, 48, 0, 0, r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), r(32, 126), 0, 0, r(40, 88), r(0, 3), r(0, 127), r(40, 88), r(0, 11), r(0, 7), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(0, 127), r(16, 112), r(16, 112), r(16, 112), r(16, 112), r(0, 7), r(0, 127), r(0, 127), r(0, 7), r(0, 127), r(0, 127), 0, 0, 0]

        op1 = [67, 0, 127, 28, 0, 32, 5, 49, 0, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(63, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        op2 = [67, 0, 127, 28, 0, 32, 5, 49, 1, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(0, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        op3 = [67, 0, 127, 28, 0, 32, 5, 49, 2, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(0, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        op4 = [67, 0, 127, 28, 0, 32, 5, 49, 3, 0, 1, 127, 127, 127, 100, 127, 127, 127, 0, r(0, 127), r(0, 127), r(0, 127), r(0, 3), r(0, 3), r(0, 127), r(0, 1), r(0, 1), r(0, 127), r(0, 127), r(0, 127), r(0, 1), r(0, 1), r(0, 31), r(0, 99), r(0, 127), 0, 0, 0]

        footer = [67, 0, 127, 28, 0, 4, 5, 15, 15, 0, 93]

        voice_settings = [com, op1, op2, op3, op4]

        for y in voice_settings:
            parameters = y[6:]
            c_sum = (sum(parameters)) % 128
            if c_sum == 127:
                c_sum = c_sum
            elif c_sum == 0:
                c_sum = c_sum
            else:   
                c_sum = 128 - c_sum
            y.append(c_sum)

        header = msg('sysex', data=header)
        com = msg('sysex', data=com)
        op1 = msg('sysex', data=op1)
        op2 = msg('sysex', data=op2)
        op3 = msg('sysex', data=op3)
        op4 = msg('sysex', data=op4)
        footer = msg('sysex', data=footer)

        sysex_messages = [header, com, op1, op2, op3, op4, footer]

        mido.write_syx_file('p' + (str(x)).zfill(2) + '.syx', sysex_messages)


def RECORD_PATCHES(port, duration, audio_input):
    print('Recording patches...\n')
    
    patches = [s for s in glob.glob('*.syx') if s.startswith('p')]

    for x in patches:
        RECORDER(x, port, duration, audio_input)
          
    print('Done!\n')      


def RECORDER(x, port, duration, audio_input):
    patch = mido.read_syx_file(x)

    for y in patch:
        port.send(y)

    note_on = msg('note_on', note=60, velocity=127)
    note_off = msg('note_off', note=60)

    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = duration

    p = pyaudio.PyAudio()

    print(f'Recording {x}')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True, input_device_index=audio_input)

    frames = []

    port.send(note_on)

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    p.terminate()

    print(f'Finished recording {x}\n')

    wf = wave.open(x.split('.')[0] + '.wav', 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()    

    port.send(note_off)
    sleep(1)


def MFCC(audio_file_data):
    print('Comparing generated patches to original audio...')

    wavs = [s for s in glob.glob('*.wav') if s.startswith('p')]

    for x in wavs:          
        analysis = subprocess.run(['aubio', 'mfcc', x],
                                  stdout=subprocess.PIPE).stdout.decode('utf-8').split()

        mfcc = []
        for y in analysis:
            mfcc.append(float(y))

        similarity = []
        for z in mfcc:
            diff = abs(z - audio_file_data[(mfcc.index(z))])
            similarity.append(diff)

        if (sum(similarity)) / (len(similarity)) == 0:
            avg = 0.00
        else:   
            avg = round(sum(similarity) / len(similarity), 3) 
   
        os.rename(x, (str(avg).replace(".", "")).ljust(4, "0") + ".wav")
        os.rename(x.split(".")[0] + ".syx",
                  (str(avg).replace(".", "")).ljust(4, "0") + ".syx")

    print('Done!\n')


def MUTATE(gen):
    print('Forming new generation...'

    prev_gen_syx = sorted([s for s in glob.glob("*.syx") if s[0].isnumeric()])
    prev_gen_wav = sorted([s for s in glob.glob("*.wav") if s[0].isnumeric()])

    best = sorted([s for s in glob.glob("*.syx") if s[0].isnumeric()])[:16]
    new_gen = best + best
    
    patch_no = -1

    for x in new_gen:
        patch_no = patch_no + 1
          
        prev_syx_file = mido.read_syx_file(x)[1:6]

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
        
        operators = [op1, op2, op3, op4]
        
        for op in operators:  
            for param in op_params:
                p = op[param]
                if p >= 102:
                    op[param] = (p - 50) + r(0, 50)
                elif p <= 25:
                    op[param] = p + r(0, 50)
                else:
                    op[param] = (p - 25) + r(0, 50)

            op[22] = r(0, 3)
            op[23] = r(0, 3)
            op[25] = r(0, 1)
            op[26] = r(0, 1)
            op[30] = r(0, 1)
            op[31] = r(0, 1)
            op[32] = r(0, 31)
            op[33] = r(0, 99)
 
        voice_settings = [com, op1, op2, op3, op4]

        for y in voice_settings:
            parameters = y[6:]
            c_sum = (sum(parameters)) % 128
            if c_sum == 127:
                c_sum = c_sum
            elif c_sum == 0:
                c_sum = c_sum
            else:   
                c_sum = 128 - c_sum
            y.append(c_sum)

        header = msg("sysex", data=header)
        com = msg('sysex', data=com)
        op1 = msg('sysex', data=op1)
        op2 = msg('sysex', data=op2)
        op3 = msg('sysex', data=op3)
        op4 = msg('sysex', data=op4)
        footer = msg('sysex', data=footer)

        syx_file = [header, com, op1, op2, op3, op4, footer]
            
        mido.write_syx_file("p" + str(patch_no).zfill(2) + ".syx", syx_file)


    new_folder = 'Gen_' + str(gen).zfill(4)
    os.mkdir(new_folder)

    for i in prev_gen_syx:
        os.rename(i, new_folder + '/' + i)

    for i in prev_gen_wav:
        os.rename(i, new_folder + '/' + i)

    print('Done!\n')


if __name__ == '__main__':
    main()
