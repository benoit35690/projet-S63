from threading import Timer
import time
import alsaaudio
import wave

class Ringtone:
    shouldring = 0
    ringtone = None
    ringfile = None

    ringstart = 0

    shouldplayhandset = 0
    handsetfile = None
    timerHandset = None

    config = None

    def __init__(self):
        print "[RINGTONE] __init__"

    def start(self):
        self.shouldring = 1
        self.ringtone = Timer(0, self.doring)
        self.ringtone.start()
        self.ringstart = time.time()

    def stop(self):
        self.shouldring = 0
        if self.ringtone is not None:
            self.ringtone.cancel()

    def starthandset(self, file):
        self.shouldplayhandset = 1
        self.handsetfile = file
        if self.timerHandset is not None:
            print "[RINGTONE] Handset already playing?"
            return

        self.timerHandset = Timer(0, self.playhandset)
        self.timerHandset.start()

    def stophandset(self):
        self.shouldplayhandset = 0
        if self.timerHandset is not None:
            self.timerHandset.cancel()
            self.timerHandset = None

    def playhandset(self):
        print "Starting dialtone"
        wv = wave.open(self.handsetfile)
        self.device = alsaaudio.PCM(device="hw:1,0")

        # Set attributes
        self.device.setchannels(wv.getnchannels())
        self.device.setrate(wv.getframerate())

        # 8bit is unsigned in wav files
        if wv.getsampwidth() == 1:
            self.device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif wv.getsampwidth() == 2:
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif wv.getsampwidth() == 3:
            self.device.setformat(alsaaudio.PCM_FORMAT_S24_LE)
        elif wv.getsampwidth() == 4:
            self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        periodsize = wv.getframerate() / 8
        self.device.setperiodsize(periodsize)

        data = wv.readframes(periodsize)
        while data and self.shouldplayhandset:
            device.write(data)
            data = wv.readframes(periodsize)
        wv.rewind()
        wv.close()

    def playfile(self, file):
        # wv = wave.open(file)
        wv = wave.open(file, 'rb')
        # self.device = alsaaudio.PCM(card="pulse")
        self.device = alsaaudio.PCM(device="hw:1,0")

        # Set attributes
        self.device.setchannels(wv.getnchannels())
        self.device.setrate(wv.getframerate())

        # 8bit is unsigned in wav files
        if wv.getsampwidth() == 1:
            self.device.setformat(alsaaudio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif wv.getsampwidth() == 2:
            self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        elif wv.getsampwidth() == 3:
            self.device.setformat(alsaaudio.PCM_FORMAT_S24_LE)
        elif wv.getsampwidth() == 4:
            self.device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        periodsize = wv.getframerate() / 8

        self.device.setperiodsize(periodsize)

        data = wv.readframes(periodsize)
        while data:
            self.device.write(data)
            data = wv.readframes(periodsize)
        wv.rewind()
        wv.close()
