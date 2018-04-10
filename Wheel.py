"""
A wheel - the robot has two

"""

import time
import math
from Constants import *

class Wheel():
    """
    A wheel class
    """
    # parameters expected
    diameter=WHEEL_DIAMETER         # mm, pixel bot size

    # calculated
    rps=0               # revs per sec controls speed + for forward - for reverse
    startTime=None      # when the RPS was changed
    distMoved=0         # since RPS changed
    totalDistMoved=0    # since last start

    moving=False

    def __init__(self,**kwargs):
        for key in kwargs:
            setattr(self,key,kwargs[key])


    def setRPS(self,rps):
        """
        Keeps track of total distance moved even if the rps
        changes

        :param float rps: revs per second
        :return None:
        """
        timeElapsed=0

        if rps>WHEEL_MAXRPS:
            print("Wheel.setRPS() rps requested=%.3f but max RPS is %.3f"%(rps,WHEEL_MAXRPS))

        rps=min(rps,WHEEL_MAXRPS)

        if rps!=0:
            if not self.moving:
                self.startTime=time.time()
                self.distMoved=0
                self.totalDistMoved=0
                self.moving=True
            else:
                # change of speed?
                # accumulate distance travelled since startTime
                now=time.time()
                timeElapsed=now-self.startTime
                self.distMoved= timeElapsed * self.rps * 2 * math.pi * self.diameter / 2
                self.totalDistMoved+=self.distMoved
                self.startTime=now
        else:
            if self.startTime is None: self.startTime=time.time()
            timeElapsed = time.time() - self.startTime
            self.distMoved = timeElapsed * self.rps * 2 * math.pi * self.diameter / 2
            self.totalDistMoved += self.distMoved
            self.moving=False

        self.rps=rps

    def getDistanceMoved(self):
        return self.totalDistMoved

    def getStatus(self):
        return self.moving

    def getRPS(self):
        return self.rps

    def getSpeed(self):
        return self.rps * math.pi * self.diameter

    def setSpeed(self,speed):
        self.setRPS(speed / math.pi * self.diameter)
