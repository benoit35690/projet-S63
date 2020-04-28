from threading import Timer
import pyaudio
import wave
import Constantes
import time

class Tonalite:

    fichierTonalite = None
    lectureActive   = 0
    lectureEnBoucle = 0
    timerLecture    = None
    pyAudio         = None
    waveFile        = None
    stream          = None

    def __init__(self):
        print "[Tonalite] __init__"
        self.pyAudio = pyaudio.PyAudio()

    def startLecture(self, fichier, boucle):
        print "[Tonalite] startLecture"
        if (self.lectureActive is not None) or\
                self.waveFile is not None or\
                self.stream is not None:
            print "[Tonalite] startLecture lecture en cours"
            self.stopLecture()
        self.lectureEnBoucle = boucle
        self.fichierTonalite = fichier
        self.waveFile = wave.open(self.fichierTonalite, 'rb')
        self.stream = self.pyAudio.open(
                                format=self.pyAudio.get_format_from_width(
                                                self.waveFile.getsampwidth()),
                                channels=self.waveFile.getnchannels(),
                                rate=self.waveFile.getframerate(),
                                output=True)
        self.lectureActive = 1
        if self.timerLecture is not None:
            print "[Tonalite] Handset already playing?"
            return

        self.timerLecture = Timer(0, self.lecture)
        self.timerLecture.start()

    def stopLecture(self):
        print "[Tonalite] stopLecture"
        if self.timerLecture is not None:
            self.timerLecture.cancel()
            self.timerLecture = None
        self.lectureActive = None

    def lecture(self):
        print "[Tonalite] lecture"
        if self.waveFile is None or\
                self.stream is None:
            print "[Tonalite] lecture ERROR"
            return

        nbchunck = 0

        while self.lectureActive:
            data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)
            while data != '' and self.lectureActive:
                tmps1 = time.time()

                self.stream.write(data)
                data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)

                nbchunck = nbchunck + 1
                tmps2 = time.time()-tmps1
                print "Temps d'execution chunk ", nbchunck, " = ", tmps2

            if self.timerLecture is not None and self.lectureEnBoucle == 1:
                print "[Tonalite] lecture rebouclage"
                self.waveFile.rewind()

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            print "[Tonalite] stream closed"
        if self.waveFile is not None:
            self.waveFile.close()
            print "[Tonalite] wave closed"
        print "[Tonalite] lecture fin de procedure"
