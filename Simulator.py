"""
Simulator.py

Responsible for updating robots

NOTE: Robot scripts are automatically run when the Robot is created

"""

from Robot import *
from Exceptions import *
import threading

# I don't know why PyCharm doesn't like this
# the module shows in the installed list
# AND it isn't highlighted in the previous demo

from smartquadtree import Quadtree

import pygame,sys
from pygame.locals import *
from ConsoleQueue import *


class Simulator():
    """
    creates a background process to update each robot

    s=Simulator(arena=(x0,y0,x1,y1)

    bot1=Robot(...)

    s.addRobot(bot1)

    """

    fps=100                  # rate at which robot update() methods are called
    robots=None             # Quadtree - robots are added using ID (name?)
    arena=None              # tuple (width,height)
    running=True
    canvas=None             # pygame canvas for drawing everything on
    canvasColor=CANVASCOLOR
    sound=Note()            # use sound.playNote(...)
    console=None

    params=None

    def __init__(self,**kwargs):
        """
        initialise the simulator
        :param kwargs:
        """
        for k,v in kwargs.items():
            setattr(self,k,v)

        assert self.arena is not None, "You must specify an arena (x0,y0,x1,y1) for the robots to operate in."
        assert type(self.arena) is tuple,"Arena must be a tuple (x0,y0,x1,y1)."

        # make sure it's big enough
        width,height=self.arena

        if (width<100) or (height<100):
            raise ArenaTooSmall("The arena seems a bit small. There would be trouble ahead... Make it bigger than "
                                "100x100")

        # create the moving object tracker
        self.robots=Quadtree(0,0,width,height)

        # required for sound mixer, must be called before pygame.init()
        #
        pygame.mixer.pre_init(44100, -16, 8, 1024)  # 8 channels (guesswork)
        pygame.init()

        self.canvas = pygame.display.set_mode((width, height),pygame.DOUBLEBUF,32)
        pygame.display.set_caption('PixelBot Simulator!')


        # kick the simulator off in a background thread
        # this lets us upload code to the robots whilst running

        self.fpsClock = pygame.time.Clock() # uses to regulate simulator speed

        #print("Simulator setup done")

    def getCanvas(self):
        return self.canvas

    def setSpeed(self,botId,lws,rws):
        bot=self.findBotById(botId)
        if bot is not None:
            console_println("Setting speed for ",bot.getName())
            bot.setSpeed(lws,rws)

    def findBotById(self,botId):
        for bot in self.robots.elements():
            if bot.getId() == botId:
                return bot
        return None


    def getRobots(self):
        return self.robots

    def addRobot(self,**kwargs):
        """
        adds a new robot to the list

        e.g. addRobot(size=20,x=30,y=34,color=0xFFFFFF,diameter=25)

        Where size is the radius of the colored disc representing the robot
        and diameter is the diameter of its wheels (mm)

        If the robot has a script it will execute immediately.

        :param kwargs: parameters for the robot
        :return None: the robot might be added to the list
        """
        params={}

        for k,v in kwargs.items():
            params[k]=v

        # also needed if not passed in

        kwargs["fps"]=self.fps
        kwargs["console"] = self.console
        kwargs["allRobots"]=self.robots

        PixBot=PixelBot(**kwargs)

        bot=self.findBotByName(PixBot.getName())
        if bot is not None:
            print(bot.getName()+"already exists. Please try again")
            return

        bot=self.findBotByColor(PixBot.getColor())
        if bot is not None:
            print(bot.getName()+"is the same color. This could get confusing. Please try again.")
            return

        self.robots.insert(PixBot)

        PixBot.run()


    def findBotByName(self,name):
        name=name.lower()
        for bot in self.robots.elements():
            if bot.getName().lower()==name.lower():
                return bot
        return None

    def findBotByColor(self,color):
        for bot in self.robots.elements():
            if bot.getColor()==color:
                return bot
        return None

    def uploadScript(self,botName,script):
        """
        Passes a script to the nominated robot

        If botId is None passes the script to ALL active robots

        :param botId: whatever id scheme you want - ints would be best
        :param script: python list ["cmooand line 0","command line 1",...,"commandline n"]
        :return None: nothing
        """
        bot=self.findBotByName(botName)
        if bot is None:
            console_println("Simulator cannot locate bot with name=",botName)
            return

        console_println("Uploading script for bot with name=",botName)
        bot.uploadScript(script)

    def stop(self):
        """
        stop the simulator loop.
        Robots are also stopped
        :return:
        """
        self.running=False

        for bot in self.robots.elements():
           bot.stop()


    def update(self):
        """
        called to update pygame from Scriptmanager.py

        caller is responsible for calling tkinter update()

        :return: Nothing
        """

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                self.running = False
                console_println("Quitting Simulation")
                for bot in self.robots.elements():
                    bot.stop()
                sys.exit()

        self.canvas.fill(self.canvasColor)

        w, h = self.arena
        pygame.draw.lines(self.canvas, (255, 255, 255), False, [(0, h / 2), (w, h / 2)], 1)
        pygame.draw.lines(self.canvas, (255, 255, 255), False, [(w / 2, 0), (w / 2, h)], 1)


        # make sure the active list contains all robots
        self.robots.set_mask(None)

        # the bots are responsible for avoiding collisions
        for bot in self.robots.elements():
            bot.update(self.canvas, self.robots)

        # this regulates the display update speed
        pygame.display.update()
        self.console.update()
        self.fpsClock.tick(self.fps)

    def getBotCount(self):
        count=0
        for bot in self.robots.elements():
            count+=1

        return count