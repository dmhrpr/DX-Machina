# DX-Machina
A Python tool which programmes your Yamaha Reface DX to sound like an audio sample you give it.


## Dependencies

- [Mido](https://pypi.org/project/mido/) *pip install mido*
- [Aubio](https://pypi.org/project/aubio/) *pip install aubio*
- [Numpy](https://pypi.org/project/numpy/) *pip install numpy*
- [PyAudio](https://pypi.org/project/PyAudio/) *pip install pyaudio*
- [python-rtmidi](https://pypi.org/project/python-rtmidi/) *pip install python-rtmidi*

### Hardware setup

Connect your audio interface and Reface DX to your computer via USB.

DX-Machina is currently set up to use USB midi only, more testing is needed to ensure that midi sysex messages are sent at the right speed when using a standard midi cable.
