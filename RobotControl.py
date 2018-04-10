"""
RobotControl.py

Called from Lex.py when Lex cannot resolve the script statement.

Handles commands which control the robot


Commands return True if the command is fully compelete
and False if the command needs more ticks to finish (timed movements)

TODO: some commands WILL need to be threaded to allow other commands to continue
TODO: thats would allow the WAIT/BACKGROUND options to work
"""

from Exceptions import *
import time
import math
from Motion import *
from ToneGenerator import *
import random
from Constants import *
import re
from Collision import *
from ConsoleQueue import *

class RobotController(object):

    cmdList=None

    robot=None
    fps=100             # used to calculate MOVE and ARC timing
    delayTill=0
    delaySet=False
    wasDelayed=False    # set if a command sets a delay
    sound=None
    arena=(0,0)
    running=True
    console=None

    def __init__(self,**kwargs):

        for k,v in kwargs.items():
            setattr(self,k,v)

        # initialise the list of available commands
        self.cmdList={}
        self.cmdList["move"]    =   self._move
        self.cmdList["turn"]    =   self._turn
        self.cmdList["sound"]   =   self._sound
        self.cmdList["arc"]     =   self._arc
        self.cmdList["angry"]   =   self._angry
        self.cmdList["happy"]   =   self._happy
        self.cmdList["delay"]   =   self._delay

        # not part of spec but useful to position
        # robot at start
        self.cmdList["pos"]     =   self._pos
        self.cmdList["dir"]     =   self._dir
        self.cmdList["angle"]   =   self._angle
        self.cmdList["compass"] =   self._compass
        self.cmdList["heading"] =   self._heading

        for color in COLORS:
            self.cmdList[color] =   self._color

        self.running=True

        # controls for intime/delay
        self.delayTill = time.time()
        self.delaySet = False
        self.wasDelayed = False
        self.arena=self.robot.getArena()

        self.sound=Note()   # used for playing sound tones

    def syntaxError(self,*args):
        """
        Output a syntax error message to the console but don't halt the program

        :param args: arguments for printing
        :return: FINISHED to allow other scripts to continue running
        """
        console_println(self.robot.getName()," - Syntax Error:",args,"at line ",self.robot.script.getLineNumber())
        return FINISHED

    def doCommand(self,command):
        """
        command is a space separated list
        :param command:
        :return:
        """
        params=command.strip().split()

        #print("RobotControl.py: doCommand ",command)

        try:
            func=self.cmdList[params[0].lower()]

            if func is None:
                return self.syntaxError("Unknown command "+" ".join(params))

            # execute the method and return a value
            return func(params)

        except KeyError:
            return self.syntaxError("Key error:",command)


    def evaluate(self,expr):
        return self.robot.lex().evaluate(expr)

    def stop(self):
        """
        Stop sets a flag so that any BACKGROUND commands terminate

        :return:
        """
        print("RobotControl stop() called.")
        self.running=False  # threads will terminate when ready

    def run(self):
        """
        Used to set a flag to allow BACKGROUND  threads to terminate
        :return:
        """
        print("RobotControl.run() called.")
        self.running=True  # threads will terminate when ready

    def _stepper(self,duration,func):
        """
        provides calls to func at fps for duration

        To be used for commands like MOVE 100 INTIME 10

        When BACKGROUND is specified this is run in a separate thread

        :param func: function to call
        :return: nothing when finished
        """
        t0=time.time()
        while (time.time()-t0)<duration:
            func()

            if not self.running:
                #print("_stepper robot not running")
                break

            t1=time.time()
            while (time.time()-t1)<(1/self.fps):
                #print("_stepper delay")
                pass

        #print("_stepper done in",time.time()-t0)

    def runMover(self,background,intime,mover):
        if background:
            t = threading.Thread(target=self._stepper, args=(intime, mover))
            t.start()
            return FINISHED

        else:
            self._stepper(intime,mover)


    # commands
    # all functions must return a value for delaying next command if not instantaneous

    def _move(self, param=None):
        """
        Moves the robot forward a given distance (mm)

        use *MV to configure wheels

        examples:
        move 100
        move -200
        move 100 intime 100 in tenths of a second

        :param [] param: move parameters
        :return:
        """
        syntax="MOVE <dist> [ INTIME <time> [BACKGROUND ]]" # BACKGROUND is ignored")

        intime=0
        background=False

        paramCount=len(param)

        if paramCount<2 or paramCount==3:
            return self.syntaxError(syntax)

        # all MOVE commands have a distance
        distance = int(param[1])    #self._getValue(param[1])

        if paramCount==2:
            # this is a hyperjump
            # real hdw might not be able to do this
            linearMove(self.robot, distance)
            return FINISHED

        if len(param)>=4:
            if param[2].lower()!= "intime":
                return self.syntaxError(syntax)

            intime=int(param[3])*0.1

        # currently not used
        # probably means return immediately whilst continuing to move
        if len(param)==5:
            background=True

        speed = distance / intime

        # the robot update is called fps times a second
        # calc deltaDistance to move
        deltaDist = speed / self.fps

        def mover():
            # for linear motion just reflect the direction 180 deg (PI radians)
            bump,hMotion,vMotion=checkWallBump(self.robot)
            if bump:
                # reverse
                self.robot.setDirection(self.robot.getDirection()+math.pi)
            linearMove(self.robot, deltaDist)

        self.runMover(background,intime,mover)

        return FINISHED

    def _turn(self,param=None):
        """

        Turn the robot through an angle in a given timer. centre is current robot x,y

        :param list param: "turn" <angle> [ "intime" <tenths of a second> [BACKGROUND]]
        :return:

        """
        syntax="TURN <angle> [ intime <movetime> [BACKGROUND] ]"

        theAngle=0
        intime=0
        background=False

        paramCount = len(param)

        if paramCount < 2 or  paramCount==3 or paramCount>=5:
            self.syntaxError(syntax)
            return FINISHED

        if paramCount>=2:
            # get angle to turn
            theAngle = int(param[1])
            theAngle= math.radians(theAngle)/2

        if paramCount == 2:
            # instantaneous turn
            self.robot.setDirection(self.robot.getDirection() + theAngle)
            return FINISHED

        if len(param) >= 4:
            if param[2].lower() != "intime":
                return self.syntaxError(syntax)

            intime = int(param[3])*0.1

        if len(param)==5 and param[4].lower()=="background":
            background=True

        speed=theAngle/intime
        deltaAngle= speed/self.fps  # proportion per tick to chnage

        def mover():
            # turning about it's centre - should not bump into walls
            self.robot.setDirection(self.robot.getDirection() + deltaAngle)

        self.runMover(background,intime,mover)

        return FINISHED

    def _arc(self,param=None):
        """

        if radius is positive the arc is to the right
        otherwise to the left

        :param param:
        :return:
        """
        syntax = "ARC radius ANGLE degrees [ INTIME duration [BACKGROUND]]"

        angle=0
        radius=0
        intime=0
        background=False

        robotX,robotY=self.robot.getPos()
        robotDirection=self.robot.getDirection()    # returns radians

        paramLen=len(param)

        if paramLen<4:
            return self.syntaxError(syntax)


        if param[2].lower()!="angle":
            return self.syntaxError(syntax)

        self.radius=float(param[1])
        angle=math.radians(abs(float(param[3])))

        # nothing to do?
        if angle==0: return

        # cx/cy are at 90 degrees to the current robot direction
        self.cx,self.cy=arcCentre(robotX,robotY,self.radius,robotDirection)

        if paramLen>4 and param[4].lower()!="intime": return self.syntaxError(syntax)
        if paramLen>=5:
            intime=int(param[5])*0.1

        if intime==0:
            # instant move along arc
            # TODO  needs to check wall bump
            ang=math.radians(angle)
            robotX=self.cx+self.radius*math.cos(ang)
            robotY=self.cy+self.radius*math.sin(ang) # drawing is top to bottom
            self.robot.setDirection(robotDirection+ang)
            self.robot.setPos((robotX,robotY))
            return

        if paramLen>6: return self.syntaxError(syntax)
        if paramLen==6 and param[5].lower()=="background":
            background=True

        deltaAngle=angle/(intime*self.fps)
        if self.radius<0:
            # reverse direction
            deltaAngle=-deltaAngle

        robotX, robotY = self.robot.getPos()
        self.turnAngle=math.radians(anglePoint(robotX, robotY, self.cx, self.cy))

        def mover():
            newDir,newCx,newCy,turnAngle=checkArcWallBump(self.robot,self.arena,self.cx,self.cy)
            if newDir is not None:
                self.robot.setDirection(newDir)
                self.cx=newCx
                self.cy=newCy
                self.turnAngle=turnAngle

            self.turnAngle= self.turnAngle + deltaAngle

            robotX = self.cx + abs(self.radius) * math.cos(self.turnAngle)
            robotY = self.cy + abs(self.radius) * math.sin(self.turnAngle) # drawing is top to bottom

            self.robot.setDirection(self.robot.getDirection() + deltaAngle)
            self.robot.setPos((robotX, robotY))

        self.runMover(background, intime, mover)

        return FINISHED

    def _sound(self,param=None):
        """

        issue a sound at a given frequency for a given time

        if frequency is zero existing sounds are stopped

        WAIT is assumed

        :param param:
        :return:
        """
        syntax="SOUND <freq> [ <duration> [ WAIT]]"

        paramCount=len(param)
        freq=0
        duration=0

        if paramCount>=2:
            freq = int(param[1])

            if freq==0 and self.sound is not None:
                self.sound.stop()
                return FINISHED

        if paramCount>=3:
            duration=int(param[2])
            if duration<=0: return FINISHED

        assert duration>0, "sound duration must be more than zero millisecs."

        # play the sound. If WAIT is specified halt progress of this bot's script
        self.sound.playNote(freq, duration=duration, type="square")  # arduino can only turn speaker on/off

        if paramCount == 4 and param[3].lower() == "wait":
            time.sleep(duration/1000)

        return FINISHED


    def _angry(self,param=None):
        self.robot.pixelRing.angry()
        return FINISHED

    def _happy(self,param=None):
        self.robot.pixelRing.happy()
        return FINISHED


    def _delay(self,param=None):
        """
        delay script execution

        :param list param: param[0]="DELAY" , param[1]=tenths of sec
        :return:
        """

        delay=float(param[1])*0.1
        time.sleep(delay)
        return FINISHED


    def _color(self,param=None):
        self.robot.setColor(param[1])
        return FINISHED


    def _pos(self,param=None):
        """
        sets the robot position - extra command not in the syntax
        :param param:
        :return: nothing the robot is hyperjumped to the required place
        """
        rx=int(param[1])
        ry=int(param[2])
        #print("Placing robot at ",rx,ry)
        self.robot.setPos((rx,ry))
        return FINISHED

    def _dir(self,param=None):
        """
        extra - set direction
        :param int param: angle in degrees - clockwise from
        zero (due East)
        :return: robot direction is set
        """
        ang = math.radians(int(param[1]))
        self.robot.setDirection(ang)

        return FINISHED


    def _angle(self,param=None):
        """
        set the robot direction
        :param param: angle direction measure from east
        :return:
        """
        # compute direction (anti-clockwise from East)
        dir=(360-int(param[1])) % 360
        self.robot.setDirection(math.radians(dir))


    def _compass(self,param=None):
        """
        Set's the robot direction based on nautical compass readings

        North=0, East=90,South=180,West=270

        :param int param: heading
        :return:
        """
        # compute direction (anti-clockwise from East)
        dir=(int(param[1])+270) % 360
        self.robot.setDirection(math.radians(dir))


    def _heading(self,param=None):
        """
        An alias for compass

        :param param: heading angle North=0, East=90,South=180,West=270
        :return:
        """
        self._compass(param)
