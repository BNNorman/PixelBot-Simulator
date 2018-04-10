"""
The pixel Ring

Basically this is drawn on top of the robot

"""

import math
import pygame
import time

class PixelRing(object):
    # parameters expected
    outerRadius=15              # outer radius of the ring
    numLeds=8                   # number of leds on pixel ring
    ledRadius=6                 # LED radius
    ledRingRadius=9             #

    # calculated
    ledColor=None               # list of Leds in the ring
    ledFlashRate=1              # flashing once per sec
    ledsOn=True


    def __init__(self,**kwargs):

        for key in kwargs.keys():
            setattr(self,key,kwargs[key])

        self.ledRingRadius=self.outerRadius-(self.ledRadius/3)

        # build the led list
        self.ledColor=[]
        self.nextLedChange = time.time()
        self.ledsOn=True

        for led in range(self.numLeds):
            self.ledColor.append(0x000000)

        # happy bot to start with
        self.happy()

    def setLedStatus(self):
        now=time.time()
        if now>=self.nextLedChange:
            self.ledsOn=not self.ledsOn
            self.nextLedChange=now+(1/self.ledFlashRate)

    def draw(self,pos,canvas):
        x,y=pos
        ledAngle = 2 * math.pi / self.numLeds

        self.setLedStatus() # on or off

        for led in range(self.numLeds):
            ledX=x+self.ledRingRadius*math.cos(ledAngle*led)
            ledY=y+self.ledRingRadius*math.sin(ledAngle*led)

            color=self.ledColor[led] if self.ledsOn else 0x000000
            pygame.draw.circle(canvas, color, (int(ledX), int(ledY)), self.ledRadius, 0)

    def angry(self,howAngry=3):
        # fast flashing red
        for led in range(self.numLeds):
            self.ledColor[led]=0xFF0000 # red

        self.ledFlashRate=howAngry  # flashes per second

    def happy(self,howHappy=2):
        # fast flashing red
        for led in range(self.numLeds):
            self.ledColor[led]=0x00FF00 # green

        self.ledFlashRate=howHappy  # flashes per second


    def sad(self,howSad=1):
        for led in range(self.numLeds):
            self.ledColor[led] = 0x0000FF  # blue

        self.ledFlashRate = howSad  # flashes per second