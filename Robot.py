"""
Robot.py

Defines the PixelBot

"""

import pygame
from Wheel import *
from PixelRing import *
from Script import *
from Lex import *
from UltraSound import *
from Collision import *
from Colors import *
from Constants import *
from ToneGenerator import *
import threading
from tkinter import messagebox

# status values defined here to stop typos


class PixelBot():

    staticID=0          # used to derive the next robot id


    # instance variables (see __init__

    name="nobody"       # name of this bot e.g. "brian"
    pos=(0,0)           # default (x,y)
    size=30             # default diameter of the bot
    direction=0         # radians , anti-clockwise (thanks pygame)

    color=None          # used to color the robot image (Should be one of the six known colors)
    allRobots=None      # used to detect collisions

    leftWheel=None      # not being used
    rightWheel=None     # not being used
    pixelRing=None      # LEDs on top of robot
    distSensor=None     # ultrasonic distance sensor simulator

    status=STOPPED

    dragging=False      # being dragged to new location (not yet implemented)

    lex=None            # lexical analyser for scripts
    fps=None            # needed by timing code in Interpreter
    lastCmdDone=True    # some commands need time

    console=None

    arena=(0,0)         # width and height

    scriptPath=None     # path to script file
    script=None         # Script object() no instructions yet

    def __init__(self,**kwargs):
        for key,value in kwargs.items():
            setattr(self,key,value)


        self.newIndent=0    # script indent

        # must be setup before script is uploaded and starts running

        self.lex = Lex(robot=self, console=self.console, fps=self.fps)

        if self.scriptPath is None:
            # no script passed in - wait for upload
            print(self.name,"no script supplied")
            self.script=Script()
        else:
            # if the script is passed in during creation
            print("Robot.__init__() script=",self.scriptPath)
            assert type(self.scriptPath) is str,"If you pass a script directly to the robot it should be a filename."
            self.script = Script()
            self.uploadScript(self.scriptPath)    # start the script running as well

        assert self.allRobots is not None,"You must pass the allRobots parameter when creating a robot so it can " \
                                          "detect any others"

        self.leftWheel=Wheel(diameter=WHEEL_DIAMETER)    # mm
        self.rightWheel=Wheel(diameter=WHEEL_DIAMETER)
        self.pixelRing=PixelRing(outerRadius=PIXELRING_OUTERRADIUS,numLeds=PIXELRING_NUMLEDS,
                                 ledRadius=PIXELRING_LEDRADIUS)


        self.lastCmdDone=True

        print("Adding distance sensor")
        self.distSensor = DistSensor()
        self.status = STOPPED if self.scriptPath is None else RUNNING
        self.dragging = False  # true if being dragged to new location (not yet implemented)
        self.lastCmdDone=True

        print("Robot",self.name,"created.")


    def serialize(self):
        """
        used to serialise the robot when saving to file
        :return: a dictionary object
        """
        return {
            'name':         self.name,
            'color':        self.color,
            'size':         self.size,
            'scriptPath':   self.scriptPath,
        }

    def getArena(self):
        return self.arena

    def replaceScript(self,theScript):
        """
        meant to be called from ScriptManager when debugging scripts
        :param theScript:
        :return:
        """
        self.stop()
        while self.status!=STOPPED:
            print("Waiting for robot to stop")
            t0=time.time()
            while (time.time()-t0)<2:
                pass

        self.script.replaceScript(theScript)
        self.run()

    def uploadScript(self,scriptPath):
        """
        reads a script from a disk file
        :param scriptPath: file pathname
        :return:
        """
        self.stop()
        self.script.uploadScript(scriptPath) # resets the linenumber

        # caller calls run - otherwise it triggers twice and plays havoc
        # with sound buffering
        # self.run()

    def setColor(self,colorName):
        self.color=getColorByName(colorName)

    def getColor(self):
        return self.color

    def setPos(self,pos):
        x,y=pos
        w,h=self.arena

        # stay within the wall collision bounds
        x=min(max(x,WALLMARGIN),w-WALLMARGIN)
        y=min(max(y,WALLMARGIN),h-WALLMARGIN)

        self.pos=(x,y)

    def getPos(self):
        return self.pos

    def getSize(self):
        return self.size

    def setSize(self,newSize):
        self.size=newSize

    # get_x and get_y are required by smartquadtree when
    # filtering the robot list

    def get_x(self):
        #x,y=self.pos
        #return x
        return self.pos[0]


    def get_y(self):
        #x,y=self.pos
        #return y
        return self.pos[1]


    def getId(self):
        return self.name

    def getName(self):
        return self.name

    def getDirection(self):
        return self.direction

    def setDirection(self,direction):
        self.direction=direction

    def getDistance(self):
        if self.allRobots is None:
            print(self.name,"allRobots is None")
            return OUTOFRANGE

        bot=self.distSensor.getNearestBot(None,self,self.allRobots)
        if bot is None: return OUTOFRANGE
        return self.distSensor.getDistance(self,bot)

    def getRange(self):
        """
        Max range of ultrasound sensor
        :return: configured range
        """
        return DISTANCESENSORRANGE  # see Constants.py

    def getSpeed(self):
        """
        for now return the average speed of each wheel
        :return float: average speed of each wheel
        """
        lws=self.leftWheel.getSpeed()
        rws=self.rightWheel.getSpeed()

        return (rws+lws)/2

    def setSpeed(self,lws,rws):
        self.status=RUNNING
        self.leftWheel.setSpeed(lws)
        self.rightWheel.setSpeed(rws)

    # drag/drop is used when the user drags a robot to a new location

    def drag(self):
        if self.dragging: return
        self.dragging=True

    def drop(self):
        self.dragging=False
        #self.x=mouse.X
        #self.y=mouse.Y
        #self.pos=(mouse.X,mouse.Y)


    def stop(self):
        print("Robot.py stop() called for",self.name)
        if self.lex is not None:
            self.lex.stop()
            self.status = STOPPED

    def run(self):

        """
        starts the robot script running in it's own thread

        This (hopefully) prevents scripts stalling.

        :return: Nothing
        """
        if self.lex is None:
            self.lex = Lex(robot=self, console=self.console, fps=self.fps)

        self.status = RUNNING
        t=threading.Thread(target=self._runScript)
        t.start()


    def avertCollision(self):
        """
        if a collision is about to occur veer 45 degrees right
        :return:
        """
        # should turn away from collision track not just
        # turn to avoid collision
        self.direction+=math.pi/4   # 45 degrees for now


    def draw(self,canvas):
        """
        Draws the robot in it's current position in the arena (canvas)

        It is called from update()

        :param Surface canvas: pygame surface
        :return: nothing
        """
        x,y=self.pos    # can be float values
        botColor=getColorByName(self.color)
        pygame.draw.circle(canvas, botColor,(int(x),int(y)), self.size, 0)
        self.pixelRing.draw(self.pos,canvas)
        self.distSensor.draw(canvas,self)

    def update(self,canvas,robots):
        """
        update is called fps times per second to update the visual display

        The robot should progress it's next/current instruction
        :param pygame.surface canvas: for drawing on
        :param Quadtree robots: list of active robots
        :return:
        """
        self.allRobots=robots   # needed for getDistance() to work
        self.draw(canvas)

        # TODO add dragging capability
        #if self.dragging:
        #    # don't progress movement till dropped
        #    return

        # check for collision between me and another bot
        nearestBot=self.distSensor.getNearestBot(canvas,self,robots)

        if nearestBot is not None:
            if nearestBot.getName()!=self.getName():
                print("nearestBot name=", nearestBot.getName())
                if haveCollided(self,nearestBot):
                    self.avertCollision()

        # check for collision with canvas walls
        checkWallBump(self)

    def _runScript(self):
        """
        A seperate thread

        The robot's script is run in a separate thread so that multiple robots
        can be running at the same time

        Called from run().

        :return: Nothing.
        """
        print(self.getName() + " Robot._runScript() starting")
        self.status=RUNNING

        # make sure we have created a Lex object to interpret commands
        if self.lex is None:
            self.lex = Lex(robot=self, console=self.console, fps=self.fps)

        if self.script is None:
            res,msg=self.script.uploadScript(self.scriptPath)
            if not res:
                messagebox.showinfo("Robot._runScript()",msg)

        # does not return till the script is stopped or finished normally
        self.lex.run()

        self.status=STOPPED
        print(self.getName()+" Robot._runScript() has terminated")