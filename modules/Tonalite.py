# -*- coding: utf-8 -*-
from threading import Timer, Lock, Thread
import pyaudio
import wave
import Constantes
import time


class Tonalite:

    # lectureActive mis a jour par startLecture et stopLecture
    lectureActive   = False
    lectureEnBoucle = 0
    worker          = None

    def __init__(self):
        print "[Tonalite] __init__"

        # demarre le thread de la class Automate
        self.worker = lectureThread()
        self.worker.start()

    def __del__(self):
        self.worker.stop()

    def startLecture(self, fichier, boucle):
        print "[Tonalite] startLecture boucle= ", boucle

        if self.lectureActive is True:
            print "[Tonalite] startLecture lecture deja en cours"
            return

        # mise à jour avec parametre du flux à jouer
        self.worker.setParameters(fichier, boucle)

        # redemarrage du thread mis en pause
        self.worker.resume()
        self.lectureActive = True

    def stopLecture(self):
        print "[Tonalite] stopLecture"
        if self.lectureActive is False:
            print "[Tonalite] stopLecture aucune lecture en cours"
            return

        self.worker.pause()
        self.lectureActive = False


class lectureThread(Thread):
    boucle = None
    pyAudio = None
    waveFile = None
    stream = None

    def __init__(self):
        Thread.__init__(self)
        self._etat = False
        self._pause = False
        self.boucle = False
        self.waveFile = None
        self.stream = None
        self.pyAudio = pyaudio.PyAudio()

    def run(self):
        self._etat = True
        while self._etat is True:
            if self._pause is True:
                if self.waveFile is not None:
                    self.waveFile.close()
                    self.waveFile = None
                if self.stream is not None:
                    self.stream.close()
                    self.stream = None
                time.sleep(0.1)  # éviter de saturer le processeur
                continue

                if self.waveFile is None or\
                   self.stream is None:
                    self.waveFile = wave.open(self.fichier, 'rb')
                    self.stream = self.pyAudio.open(
                                    format=self.pyAudio.get_format_from_width(
                                                self.waveFile.getsampwidth()),
                                    channels=self.waveFile.getnchannels(),
                                    rate=self.waveFile.getframerate(),
                                    output=True)

            self.data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)
            if self.data == '' and self.boucle is True:
                print "[lectureThread] run rebouclage"
                self.waveFile.rewind()
                self.data = self.waveFile.readframes(Constantes.AUDIO_CHUNK)
            if self.data is not None and self.data != '':
                self.stream.write(self.data)

        print "[lectureThread] run fin de procedure"

    def stop(self):
        """ Arrête l'exécution du thread.
            Après avoir appelé cette fonction le thread n'est plus utilisable.
        """
        print "[lectureThread] stop"
        self._etat = False

    def pause(self):
        """ Arrête l'exécution du thread momentanément."""
        print "[lectureThread] pause"
        if self._pause is True:
            print "[lectureThread] Thread déjà en pause"
            return

        self._pause = True

    def resume(self):
        """ Reprendre l'exécution d'un thread 'mis en pause'."""
        print "[lectureThread] resume"
        if self._pause is False:
            print "[lectureThread] Thread déjà en fonctionnement"
            return

        self._pause = False

    def setParameters(self, fichier, boucle):
        """ Fixe les parametres de lecture (fichier et rebouclage)"""
        print "[lectureThread] setParameters"

        self._pause = True
        self.boucle = boucle
        self.fichier = fichier
