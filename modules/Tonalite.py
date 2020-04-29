# -*- coding: utf-8 -*-
from threading import Timer, Lock, Thread
import pyaudio
import wave
import Constantes
import time

class Tonalite:

    # lectureActive mis a jour par startLecture et stopLecture
    lectureActive   = None
    lectureEnBoucle = 0
    worker          = None
    pyAudio         = None
    waveFile        = None
    stream          = None

    def __init__(self):
        print "[Tonalite] __init__"
        # demarre le thread de la class Automate
        self.worker = Thread(target=self.lecture)
        self.worker.setDaemon(False)

        self.mutex = Lock()
        self.pyAudio = pyaudio.PyAudio()

    def startLecture(self, fichier, boucle):
        print "[Tonalite] startLecture boucle= ", boucle

        if self.lectureActive is not None
            print "[Tonalite] startLecture lecture en cours"
            return

        # mise à jour avec parametre du flux à jouer
        self.lectureEnBoucle = boucle

        # ouverture du flux à jouer
        self.waveFile = wave.open(fichier 'rb')
        self.stream = self.pyAudio.open(
                                format=self.pyAudio.get_format_from_width(
                                            self.waveFile.getsampwidth()),
                                channels=self.waveFile.getnchannels(),
                                rate=self.waveFile.getframerate(),
                                output=True)

        self.lectureActive = 1
        self.worker.start()

    def stopLecture(self):
        print "[Tonalite] stopLecture"
        self.lectureActive = None

        print "[Tonalite] stopLecture attente fin du thread"
        self.worker.join()
        print "[Tonalite] stopLecture joint passe"

    def lecture(self):
        # wave file can be closed outside of this thread by
        print "[Tonalite] lecture ", \
            " boucle = ", self.lectureEnBoucle

        while self.lectureActive is not None:
            # ce while sert a gerer le rebouclage
            if self.waveFile is not None:
                self.data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)

            while self.data is not None and\
                    self.data != '' and\
                    self.lectureActive is not None:
                if self.stream is not None and\
                     self.waveFile is not None:
                    #print "[Tonalite] lecture stream.write"
                    if self.data is None or self.data == '':
                        print "[Tonalite] lecture self.data is None"
                    self.stream.write(self.data)
                    self.data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)

            if self.waveFile is not None and\
               self.lectureEnBoucle == 1:
                print "[Tonalite] lecture rebouclage"
                self.waveFile.rewind()
            else:
                self.lectureActive = None

            # end while lectureActive

        print "[Tonalite] lecture fin de procedure"
