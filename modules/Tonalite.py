from threading import Timer
import pyaudio
import wave
import Constantes


class Tonalite:

    fichierTonalite = None
    lectureActive   = 0
    timerLecture    = None

    def __init__(self):
        print "[Tonalite] __init__"

    def startLecture(self, fichier):
        if self.lectureActive == 1:
            self.stopLecture()

        self.lectureActive = 1
        self.fichierTonalite = fichier
        if self.timerLecture is not None:
            print "[RINGTONE] Handset already playing?"
            return

        self.timerLecture = Timer(0, self.lecture)
        self.timerLecture.start()

    def stopLecture(self):
        self.lectureActive = 0
        if self.timerLecture is not None:
            self.timerLecture.cancel()
            self.timerLecture = None

    def lecture(self):
        print "[Tonalite] play"

        wf = wave.open(self.fichierTonalite, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        while self.lectureActive:
            data = wf.readframes(Constantes.AUDIO_CHUNK)
            while data != '' and self.lectureActive:
                stream.write(data)
                data = wf.readframes(Constantes.AUDIO_CHUNK)
            wf.rewind()

        stream.stop_stream()
        stream.close()
        wf.rewind()
        wf.close()
