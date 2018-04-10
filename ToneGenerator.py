# Generate a 440 Hz square waveform in Pygame by building an array of samples and play
# it for 5 seconds.  Change the hard-coded 440 to another value to generate a different
# pitch.
#
# Run with the following command:
#   python pygame-play-tone.py
#
# from: https://gist.github.com/ohsqueezy/6540433
#
# PyGame supports 8 mixer channels

from array import array
from time import sleep
import sys
import numpy
import pygame
import threading
import time
from Exceptions import *

from pygame.mixer import Sound, get_init, pre_init


class Note(Sound):
    frequency=10
    duration=1000   # millisec
    sampler=None
    volume=0.1
    queue=None        # sequence of notes to play one after the other
    queuePlaying=False

    def __init__(self):
        #pygame.mixer.Sound.__init__(self, buffer=self.build_square_samples())
        #super().__init__(self,*args)
        self.queue=[]
        self.queuePlaying=False
        self.volume = 0 # keep quiet till ready

    def addToQueue(self,freq,duration):
        """
        addToQueue allows the robot script to play notes in sequence whilst getting on
        doing it's own thing and not waiting

        :param freq:
        :param duration:
        :return:
        """
        self.queue.append((freq,duration))

    def playQueue(self):
        while self.queuePlaying:
            pass
        t=threading.Thread(target=self._playQueue)
        t.start()

    def _playQueue(self):
        self.queuePlaying=True
        while len(self.queue)>0:
            n,d=self.queue[0]
            self.queue=self.queue[1:]
            self.playNote(n,d)
        self.queuePlaying=False


    def playNote(self, frequency, duration=1000,type="sine", volume=.1):
        self.volume=volume
        self.frequency = frequency
        # wait till previous sound has finished??
        while pygame.mixer.get_busy():
            pass

        if type=="sine":
            pygame.mixer.Sound.__init__(self, buffer=self.build_sine_samples())
        else:
            pygame.mixer.Sound.__init__(self, buffer=self.build_square_samples())

        # duration should be in millisecs
        # loop until duration has expired otherwise you get a short burst
        self.play(loops=-1,maxtime=int(duration))
        self.set_volume(self.volume)

    def build_square_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

    def build_sine_samples(self):
        sample_rate = pygame.mixer.get_init()[0]
        period = int(round(sample_rate / self.frequency))
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1

        def frame_value(i):
            return amplitude * numpy.sin(2.0 * numpy.pi * self.frequency * i / sample_rate)

        return numpy.array([frame_value(x) for x in range(0, period)]).astype(numpy.int16)

    def stop(self):
        pygame.mixer.Sound.stop()

if __name__ == "__main__":
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    pygame.display.set_mode((100,100))
    print("Should be playing a note")
    t0=time.time()
    N=Note(440,duration=5,type="sine")
    t1=time.time()
    print("Note stopped after",t1-t0,"secs")
    sleep(7)
    print("Stopped")
