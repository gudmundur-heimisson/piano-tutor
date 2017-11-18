from itertools import chain
from functools import partial
from pyo import *

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
note_array = [note_names[i % 12] for i in range(128)]

class ChordHandler:

    def __init__(self):
        self.active = []
    
    def noteOn(self, note, velocity=None):
        self.active.append(note)

    def noteOff(self, note, velocity=None):
        self.active.remove(note)


def process_raw_midi(status, byte1, byte2, ch=None):
    if status == 128:
        # Note Off
        ch.noteOff(byte1, byte2)
    elif status == 144:
        # Note On
        ch.noteOn(byte1, byte2)
    print('-'.join(note_array[note] for note in ch.active) if ch.active else 'Rest')

ch = ChordHandler()
s = Server(audio='jack')
s.setMidiInputDevice(3)
s.boot()
s.start()
a = RawMidi(partial(process_raw_midi, ch=ch))

