"""
UltraSound.py

Ultrasonic sensor simulator for PixelBot simulator

"""

import pygame,sys
from pygame.locals import *
from smartquadtree import Quadtree
import random
import math
from Robot import *

class DistSensor():
    """
    sensor operation uses a Quadtree (see smartquadtree) with masking to create a list
    of bots within the sensor range (if any).

    This requires that bots are added to the quadtree by the controller.

    When another bot enters the sensor area a (red) line is drawn from this bot to that bot.

    drawSensorROI() will draw the sensor detection zone (in yellow) facing in the direction
    the PixelBot is moving.

    TODO: add code to determine if the distance between bots is widening or narrowing
    and concentrate only on the latter

    """

    # values used to draw the colored sensor active range
    # which is a yellow arc
    spread=30           # arc angle of sonar sensor for drawing
    range=100           # max sensing distance (radius)
    arcSteps=10         # used to calculate the ROI cordinates
    roiColor=SONARCOLOR   # dark yellow cone

    #
    drawLines=True          # draw lines joining bots within the sensor range
    lineColor=INRANGECOLOR      # red lines connect robots in range
    nearestColor=NEARESTCOLOR   # blue line conencts to nearest

    def __init__(self,**kwargs): #botList,canvas,thisBot,drawLine=True,lineColor=0xFF0000):
        """
        initialise the ultrasonic sensor.

        :param Quadtree botList: the list of active robots (pointers)
        :param Quadtree thisBot: pointer
        :param surface canvas: pygame surface to draw on if drawLine=True
        :param int lineColor: hex color for line (0xRRGGBB)
        """
        for key,value in kwargs.items():
            setattr(self,key,value)


    def updateBotList(self,botList):
        """
        not sure if this is needed..
        :param botList:
        :return:
        """
        self.botList=botList

    def draw(self,canvas,thisBot):
        """
        Draw the region of interest in front of the bot.
        :return None:
        """
        lines=self.getROI(thisBot)
        pygame.draw.polygon(canvas,self.roiColor,lines,0)


    def getROI(self,thisBot):
        """
        ROI is the reflection cone in front of the sensor mounted on the front of the bot

        calculate the poly coords for the space covered by the ultrasonic sensor

        This is used to draw the sensor's region of interest (a cone) and to provide
        a mask which excludes bots outside that cone

        ROI is a list of XY tuples

        :return list: e.g. [(x0,y0),...(xn,yn)]
        """

        # start point
        # add 1 to current X&Y to try to exclude self from
        # list which Quadtree produces using this roi as a mask
        bot_x=thisBot.get_x()+1
        bot_y=thisBot.get_y()+1
        roi=[(int(bot_x),int(bot_y))]

        # number of steps to give a reasonably smooth search light arc
        # in front of the bot

        angleStep=math.radians(self.spread/self.arcSteps)
        for curvePoint in range(self.arcSteps+1):        # gives 0 to arcSteps
            curvePoint=curvePoint-(self.arcSteps/2)      # make it go - to +

            angle=thisBot.getDirection()+curvePoint*angleStep

            x = int(bot_x + self.range * math.cos(angle))
            y = int(bot_y + self.range * math.sin(angle))
            roi.append((x,y))

        return roi


    def getDistance(self,me,him):
        """
        calculate the distance between thisBot and bot n

        :param PixelBot me: my bot object
        :param PixelBot him: his bot object
        :return : distance between us
        """

        # ignore myself
        if me.getName()==him.getName(): return OUTOFRANGE

        x0, y0 = me.getPos()
        x1, y1 = him.getPos()

        dx=(x1-x0)
        dy=(y1-y0)

        return math.sqrt( dx*dx+dy*dy)


    def getNearestBot(self,canvas,me,activeBots):
        """

        Applies the ROI to the list of activeBots
        then finds the nearest distance

        :param pygame.Surface canvas: Used to draw connecting lines. None is no lines to draw.
        :param Robot element me: this bot
        :param Quadtree activeBots: list of active bots
        :return Robot: nearest bot or None
        """

        if activeBots is None:
            print("UltraSound.getNearestBot() activeBots is None")
            return

        nearest=None    # distance to a bot
        bot=None        # the bot

        # only select those in the ROI of the sensor
        activeBots.set_mask( self.getROI(me))

        # look for nearest
        for n in activeBots.elements():
            # calculate the distance
            dist=self.getDistance(me,n)
            if nearest is None:
                nearest=dist
                bot=n
            elif dist<nearest:
                nearest=dist
                bot=n

            # draw a red line connecting me and the 'inrange' bots as they move
            if canvas is not None and self.drawLines and n.getName()!=me.getName():
                pygame.draw.line(canvas, self.lineColor,(me.get_x(),me.get_y()),(n.get_x(),n.get_y()),5)

        # remove the mask
        activeBots.set_mask(None)

        # draw a blue line to nearest
        if canvas is not None and self.drawLines and bot is not None:
            pygame.draw.line(canvas, self.nearestColor, (me.get_x(), me.get_y()), (bot.get_x(), bot.get_y()), 5)

        return bot