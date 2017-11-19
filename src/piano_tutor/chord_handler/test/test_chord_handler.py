import unittest
from unittest import TestCase
from unittest.mock import Mock, MagicMock, call, create_autospec
from functools import partial
from time import sleep
from pyo import Server, RawMidi
from piano_tutor.chord_handler import ChordHandler, process_raw_midi, NOTE_ON, NOTE_OFF

class ChordHandlerTest(TestCase):

    def setUp(self):
        self.server = Server(audio='jack')
        self.server.setMidiInputDevice(99)
        self.server.boot()
        self.server.start()
        self.chord_handler = ChordHandler()
        self.mock_chord_handler = create_autospec(ChordHandler)
        self.callback = MagicMock(side_effect=process_raw_midi)
        self.raw_midi = RawMidi(partial(self.callback, handler=self.mock_chord_handler))

    def add_midi_event(self, status, data1, data2):
        self.server.addMidiEvent(status, data1, data2)
        sleep(0.1)

    def test_raw_midi_cb(self):
        self.add_midi_event(NOTE_ON, 5, 5)
        self.callback.assert_called_once_with(NOTE_ON, 5, 5, handler=self.mock_chord_handler)

    def test_raw_midi_multiple_cb(self):
        self.add_midi_event(NOTE_ON, 7, 2)
        self.add_midi_event(NOTE_ON, 0, 0)
        self.add_midi_event(NOTE_OFF, 6, 8)
        self.callback.assert_has_calls([call(NOTE_ON, 7, 2, handler=self.mock_chord_handler),
                                        call(NOTE_ON, 0, 0, handler=self.mock_chord_handler),
                                        call(NOTE_OFF, 6, 8, handler=self.mock_chord_handler)])

    def test_process_raw_midi_note_on(self):
        self.add_midi_event(NOTE_ON, 4, 6)
        self.mock_chord_handler.noteOn.assert_called_once_with(4, 6)

    def test_process_raw_midi_note_off(self):
        self.add_midi_event(NOTE_OFF, 4, 6)
        self.mock_chord_handler.noteOff.assert_called_once_with(4, 6)

    def test_chord_handler_notes_on(self):
        self.chord_handler.noteOn(7)
        self.chord_handler.noteOn(15)
        self.chord_handler.noteOn(22)
        self.assertListEqual(self.chord_handler.active, [7, 15, 22])
        self.chord_handler.active = [5, 6]
        self.chord_handler.noteOn(7)
        self.assertListEqual(self.chord_handler.active, [5, 6, 7])

    def test_chord_handler_note_off(self):
        self.chord_handler.active = [5]
        self.chord_handler.noteOff(5)
        self.assertListEqual(self.chord_handler.active, [])
        self.chord_handler.active = [5,6,7]
        self.chord_handler.noteOff(5)
        self.assertListEqual(self.chord_handler.active, [6, 7])

    def test_chord_handler_notes_off(self):
        self.chord_handler.active = [5, 6, 7]
        self.chord_handler.noteOff(5)
        self.chord_handler.noteOff(6)
        self.chord_handler.noteOff(7)
        self.assertListEqual(self.chord_handler.active, [])
        self.chord_handler.active = [8, 9, 10]
        self.chord_handler.noteOff(10)
        self.chord_handler.noteOff(9)
        self.assertListEqual(self.chord_handler.active, [8])

    def tearDown(self):
        self.server.stop()
        self.server.shutdown()


if __name__ == '__main__':
    unittest.main()
