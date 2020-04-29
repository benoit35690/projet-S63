# -*- coding: utf-8 -*-
from threading import Timer, Lock
import pyaudio
import wave
import Constantes
import time

class Tonalite:

    # lectureActive mis a jour par startLecture et stopLecture
    lectureActive   = None

    fichierTonalite = None
    lectureEnBoucle = 0
    mutex           = None
    timerLecture    = None
    pyAudio         = None
    waveFile        = None
    stream          = None

    def __init__(self):
        print "[Tonalite] __init__"
        self.mutex = Lock()
        self.pyAudio = pyaudio.PyAudio()

    def startLecture(self, fichier, boucle):
        print "[Tonalite] startLecture boucle= ", boucle
        self.mutex.acquire()
        try:
            if (self.lectureActive is not None) or\
                    self.waveFile is not None or\
                    self.stream is not None:
                print "[Tonalite] startLecture lecture en cours"

                # on ferme d'abord le flux en cours
                self.stream.stop_stream()
                self.stream.close()
                print "[Tonalite] stream closed"
                self.waveFile.close()
                print "[Tonalite] wave closed"
                self.lectureEnBoucle = None
                self.fichierTonalite = None
                self.lectureActive   = None

            # mise à jour avec parametre du flux à jouer
            self.lectureEnBoucle = boucle
            self.fichierTonalite = fichier

            # ouverture du flux à jouer
            self.waveFile = wave.open(self.fichierTonalite, 'rb')
            self.stream = self.pyAudio.open(
                                    format=self.pyAudio.get_format_from_width(
                                                self.waveFile.getsampwidth()),
                                    channels=self.waveFile.getnchannels(),
                                    rate=self.waveFile.getframerate(),
                                    output=True)

            if self.timerLecture is not None:
                print "[Tonalite] thread de lecture deja demarre"
            else:
                # demarage du thread de lecture
                print "[Tonalite] demarage du thread de lecture"
                self.timerLecture = Timer(0, self.lecture)
                self.timerLecture.start()

            self.lectureActive = 1
        finally:
            self.mutex.release()

    def stopLecture(self):
        print "[Tonalite] stopLecture"
        self.mutex.acquire()
        try:
            # arret du thread de lecture
            if self.timerLecture is not None:
                self.timerLecture.cancel()
                self.timerLecture = None

            # fermeture du flux
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                print "[Tonalite] stopLecture stream closed"

            # fermeture du fichier
            if self.waveFile is not None:
                self.waveFile.close()
                self.waveFile = None
                print "[Tonalite] stopLecture wave closed"

            self.lectureActive = None
        finally:
            self.mutex.release()

    def lecture(self):
        # wave file can be closed outside of this thread by
        print "[Tonalite] lecture fichier = ", self.fichierTonalite, \
            " boucle = ", self.lectureEnBoucle

        lectureActive = None
        self.mutex.acquire()
        try:
            lectureActive = self.lectureActive
        finally:
            self.mutex.release()

        while lectureActive is not None:
            # ce while sert a gerer le rebouclage
            data = None
            self.mutex.acquire()
            try:
                if self.waveFile is not None:
                    data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)
            finally:
                self.mutex.release()

            while data is not None and\
                    data != '' and\
                    lectureActive:
                self.mutex.acquire()
                try:
                    if self.stream is not None and\
                         self.waveFile is not None:
                        self.stream.write(data)
                        data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)
                        lectureActive = self.lectureActive
                finally:
                    self.mutex.release()

            self.mutex.acquire()
            try:
                if self.waveFile is not None and\
                   self.timerLecture is not None and\
                   self.lectureEnBoucle == 1:
                    print "[Tonalite] lecture rebouclage"
                    self.waveFile.rewind()
            finally:
                self.mutex.release()

            # end while lectureActive

        print "[Tonalite] lecture fin de procedure"
