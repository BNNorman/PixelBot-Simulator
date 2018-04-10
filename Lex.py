import re
import Exceptions
import sys,traceback
import random
from Constants import *
from RobotControl import *
from Script import *
from ConsoleQueue import *

class Lex():

    robot=None  # provides pointer to hardware and script
    lastCmdDone=True
    globals=None
    fps=10
    machineControl=None
    running=True
    terminated=False        # flag used when the script has actually stopped
    console=None

    # used by DoNextStatement()
    lastIndent=0
    lastStatement=None

    # never change, saves changing case
    # commands may be indented AND may be followed by comments
    # command words are terminated when a none Alpha character is encountered
    reBreakContinue = re.compile(r"^\s*(break|continue)[^a-zA-Z]", re.IGNORECASE)
    reBreak         = re.compile(r"^\s*(break)[^a-zA-Z]", re.IGNORECASE)
    reContinue      = re.compile(r"^\s(continue)$", re.IGNORECASE)
    reWhile         = re.compile(r"^\s*(while)[^a-zA-Z]", re.IGNORECASE)
    reIf            = re.compile(r"^\s*(if)[^a-zA-Z]", re.IGNORECASE)
    reElse          = re.compile(r"^\s*(else)$", re.IGNORECASE)
    reForever       = re.compile(r"^\s*(forever)$", re.IGNORECASE)
    reSet           = re.compile(r"^\s*(set)[^a-zA-Z]", re.IGNORECASE)
    reIndent        = re.compile(r"^(\s*)(.*)$", re.IGNORECASE) # splits the indent from the rest of the line
    rePrint         = re.compile(r"^\s*(print)[^a-zA-Z]", re.IGNORECASE)
    rePrintln       = re.compile(r"^\s*(println)[^a-z-A-Z]", re.IGNORECASE)
    reEnd           = re.compile(r"^\s*(end)[^a-zA-Z]", re.IGNORECASE)
    reBegin         = re.compile(r"^\s*(begin)[^a-zA-Z]", re.IGNORECASE)

    reEOF           = re.compile(r"^EOF$",re.IGNORECASE)

    # extras

    #reBreadcrumb    = re.compile(r"\s*(breadcrumb)")

    # dynamic variables @<name>
    reDistance      = re.compile(r".*(@distance)[^a-zA-Z]",re.IGNORECASE)
    reRange         = re.compile(r".*(@range)[^a-zA-Z]", re.IGNORECASE)
    reLight         = re.compile(r".*(@light)[^a-zA-Z]",re.IGNORECASE)
    reMoving        = re.compile(r".*(@moving)[^a-zA-Z]",re.IGNORECASE)
    reRandom        = re.compile(r".*(@random)[^a-zA-Z]",re.IGNORECASE)
    reName          = re.compile(r".*(@name)[^a-zA-Z]",re.IGNORECASE)
    reAngle         = re.compile(r".*(@angle)[^a-zA-Z]", re.IGNORECASE)
    reCompass       = re.compile(r".*(@compass)[^a-zA-Z]", re.IGNORECASE)
    reX             = re.compile(r".*(@x)[^a-zA-Z]", re.IGNORECASE)
    reY             = re.compile(r".*(@y)[^a-zA-Z]", re.IGNORECASE)

    foreverStack=[]
    whileStack=[]

    def __init__(self,**kwargs):
        #print("Lex.__init__() starting..")

        for key,value in kwargs.items():
            setattr(self,key,value)

        self.globals={}
        self.loopCount=0
        self.beginCount=0

        #assert self.console is not None,"A console is required."

        #print("Lex.__init__() adding robot controller")
        self.machineControl=RobotController(robot=self.robot, fps=self.fps,console=self.console)

        self.terminated=True
        #print("Lex.__init__() finished")

    def Error(self,msg):
        #print(self.robot.getName() + " ERROR:", msg, ".At line ", self.robot.script.getLineNumber())
        console_println(self.robot.getName()+" ERROR:", msg, ".At line ", self.robot.script.getLineNumber())
        #exit(1)

    def Warn(self, msg):
        console_println(self.robot.getName()+" WARNING:",msg, ".At line ", self.robot.script.getLineNumber())

    def nextInstruction(self):
        """
        returns the next script instruction

        if the end of script is encountered return EOF

        :return: next instruction or EOF
        """

        if not self.running:
            print("Lex.nextInstruction() Script is not running")
            return EOF

        source= self.robot.script.getNextInstruction()
        if source is None:
            print("Lex.nextInstruction() source is None")
            return EOF
        return source

    def setLineNumber(self,lineNum):
        self.robot.script.setLineNumber(lineNum)

    def getLineNumber(self):
        return self.robot.script.getLineNumber()

    def getIndent(self,sourceLine):

        #print("getIndent sourceLine=",sourceLine)
        m = self.reIndent.match(sourceLine)
        if m:
            g1 = m.group(1)
            g2 = m.group(2)
            g1 = g1.replace("\t", " " * TABLENGTH)
            return len(g1), g2
        else:
            return 0, sourceLine

    def Statement(self, thisIndent, statement):
        """
        All scripts are treated as non-indented statements
        till FOREVER, WHILE, BEGIN or IF are found

        :param thisIndent:
        :param statement:
        :return:
        """
        #print("Statement=",statement)

        if not self.running:
            #print("NOT running")
            return 0,EOF

        if self.reIf.match(statement):
            condition=statement[2:]
            return self._if(thisIndent,condition)

        elif self.reForever.match(statement):
            return self._forever(thisIndent)

        elif self.reWhile.match(statement):
            condition=statement[5:]
            return self._while(thisIndent,condition)

        elif self.rePrint.match(statement):
            expression=statement[5:]
            return self._print(expression)

        elif self.rePrintln.match(statement):
            expression=statement[7:]
            return self._println(expression)

        elif self.reContinue.match(statement):
            if self.loopCount==0:
                self.Warn("Unexpected 'continue' ignored")
                newIndent,statement=self.getIndent(self.nextInstruction())
                return self.Statement(newIndent,statement)
            return self._continue(thisIndent)

        elif self.reEnd.match(statement):
            if self.beginCount==0:
                self.Warn("Unexpected 'end' ignored")
                newIndent,statement=self.getIndent(self.nextInstruction())
                return self.Statement(newIndent,statement)
            return self._end(thisIndent)

        elif self.reBreak.match(statement):
            if self.loopCount==0:
                self.Warn("Unexpected 'break' ignored")
                newIndent, statement = self.getIndent(self.nextInstruction())
                return self.Statement(newIndent,statement)
            return self._break(thisIndent)

        elif self.reSet.match(statement):
            return self._set(thisIndent,statement[3:])

        elif self.reElse.match(statement):
            return self._else(thisIndent)

        elif self.reEOF.match(statement):
            self.Error("EOF")

        else:
            # only machine instructions MOVE,ANGRY,HAPPY,SOUND etc are allowed
            self.lastCmdDone=self.machineControl.doCommand(statement)
            # machine control does not change the indent
            return self.getIndent(self.nextInstruction())

    def skipIndentedStatements(self,thisIndent):
        newIndent,statement=self.getIndent(self.nextInstruction())

        while newIndent>thisIndent:
            newIndent, statement = self.getIndent(self.nextInstruction())

        return newIndent,statement

    def indentedStatement(self,thisIndent):
        """
        handles statements which are expected to be indented

        Terminates when an outdented statement is encountered

        :param int thisIndent: current indent level
        :return tuple: (newIndent,statement)
        """

        newIndent,statement=self.getIndent(self.nextInstruction())

        while newIndent>thisIndent:

            #print(self.robot.getName()+" indentedStatement thisIndent=",thisIndent,"newIndent=",newIndent,
            #      "statement=",statement)

            # end of script terminates an indented statement
            if self.reEOF.match(statement):
                return newIndent, statement

            # break or continue - but may not be inside a loop
            if self.reBreakContinue.match(statement):
                return newIndent, statement

            newIndent,statement=self.Statement(newIndent, statement)


        # ok we've backed out of the indenting

        return newIndent,statement

    # break/end/continue/else
    # simply return themselves so caller can check

    def _break(self,thisIndent):
        self.loopCount-=1
        return thisIndent,"break"

    def _continue(self,thisIndent):
        return thisIndent,"continue"

    def _end(self,thisIndent):
        self.beginCount-=1
        return thisIndent,"end"

    def _else(self,thisIndent):
        return thisIndent,"else"

    # @variables

    def _distance(self):
        return self.robot.getDistance()

    def _range(self):
        return self.robot.getRange()

    def _light(self):
        return 0

    def _random(self):
        return random.randint(1,12)

    def _moving(self):
        if self.robot.getSpeed()>0: return True
        return False

    def _name(self):
        return self.robot.getName()

    def _angle(self):
        """
        returns the angle of the direction the robot is pointing in
        measured anti-clockwise from East

        :return:
        """

        # robot getDirection() is clockwise from east

        dir=math.degrees(self.robot.getDirection())
        return int(360-dir) % 360

    def _compass(self):
        """
        Compass is 360 degrees clockwise from North

        :return:
        """
        dir = math.degrees(self.robot.getDirection())
        return int(dir+90) % 360

    def _x(self):
        return int(self.robot.get_x())

    def _y(self):
        return int(self.robot.get_y())

    # normal statements

    def _EvalExpression(self,expr):
        """
        Uses pythjon's eval() to evaluate an expression.

        Before doing so it resolves @<varnam> variables

        :param expr:
        :return: value of expr
        """

        #print ("Lex._EvalExpression() before expr=",expr)

        r = self.reX.match(expr)
        if r:
            expr = expr.replace(r.group(1), str(self._x()))

        r = self.reY.match(expr)
        if r:
            expr = expr.replace(r.group(1), str(self._y()))

        r = self.reAngle.match(expr)
        if r:
            expr = expr.replace(r.group(1), str(self._angle()))

        r = self.reCompass.match(expr)
        if r:
            expr = expr.replace(r.group(1), str(self._compass()))

        r=self.reDistance.match(expr)
        if r:
            expr=expr.replace(r.group(1),str(self._distance()))

        r = self.reRange.match(expr)
        if r:
            expr = expr.replace(r.group(1), str(self._range()))

        r = self.reLight.match(expr)
        if r:
            expr=expr.replace(r.group(1), str(self._light()))

        r = self.reMoving.match(expr)
        if r:
            expr=expr.replace(r.group(1), str(self._moving()))
        r = self.reRandom.match(expr)

        if r:
            expr=expr.replace(r.group(1), str(self._random()))

        r = self.reName.match(expr)
        if r:
            expr=expr.replace(r.group(1), str(self._name()))

        #print ("Lex._EvalExpression() after expr=",expr)

        return eval(expr, self.globals)

    def _print(self,expression):
        console_print(self.robot.getName(), ":", self._EvalExpression(expression))
        return self.getIndent(self.nextInstruction())

    def _println(self,expression):
        console_println(self.robot.getName(), ":", self._EvalExpression(expression))
        return self.getIndent(self.nextInstruction())

    def _begin(self,thisIndent):
        self.beginCount+=1
        newIndent,statement=self.getIndent(self.nextInstruction())
        if newIndent<=thisIndent:
            self.Error("BEGIN should be followed by an indented statement.")
        newIndent,statement=self.Statement(newIndent, statement)

        while newIndent>thisIndent:
            newIndent,statement=self.indentedStatement(newIndent)

        if not self.reEnd.match(statement):
            self.Error("Expected END")

        self.beginCount-=1
        return newIndent,statement

    def _if(self,thisIndent,condition):
        result=self._EvalExpression(condition)

        if result:
            # do the indented 'then' statements
            newIndent,statement=self.indentedStatement(thisIndent)

            # skip the 'else' clause if there is one
            if self.reElse.match(statement):
                newIndent,statement=self.skipIndentedStatements(thisIndent)

        else:
            # skip the 'then' clause
            newIndent,statement=self.skipIndentedStatements(thisIndent)

            # process the ELSE clause if there is one
            r=self.reElse.match(statement)
            if r:
                newIndent, statement = self.indentedStatement(newIndent)

        return newIndent,statement

    def _while(self,thisIndent,condition):

        self.loopCount+=1
        # need to know where to go back to
        self.whileStack.append(self.getLineNumber())
        newIndent=0

        while True:
            r=eval(condition,self.globals)
            # end of while loop
            if not r:
                r=self.whileStack.pop()   # throw away
                return self.skipIndentedStatements(thisIndent)

            # the first statement following the while
            newIndent,statement=self.indentedStatement(thisIndent)

            while newIndent > thisIndent:

                # break
                if self.reBreak.match(statement):    #statement[:5].lower()=="break":
                    # skip everything
                    r=self.whileStack.pop()
                    return self.skipIndentedStatements(newIndent)

                #continue - back to while statement
                elif self.reContinue.match(statement):
                    self.setLineNumber(self.whileStack.pop())
                    newIndent=thisIndent
                    break

                else:
                    newIndent,statement=self.Statement(newIndent, statement)

            # indented statements have been done
            # go back to the beginning
            self.setLineNumber(self.whileStack.pop())
            newIndent = thisIndent
            return thisIndent,statement

    def _forever(self, thisIndent):
        """
        statement will be FOREVER so
        :param thisIndent:
        :return:
        """
        # need to know where to go back to
        #print(self.robot.getName()+" FOREVER starts thisIndent=",thisIndent," at line ",self.getLineNumber())

        self.foreverStack.append(self.getLineNumber())
        self.loopCount -= 1

        # this should consume all indented lines unless a break/continue/EOF occurs

        newIndent, statement = self.indentedStatement(thisIndent)

        #print(self.robot.getName()+" FOREVER finishes indented statements with indent",newIndent,"statement=",
        #      statement," at line ",self.getLineNumber())

        # find out what statement terminated the forever

        self.loopCount-=1

        if newIndent<=thisIndent:
            self.setLineNumber(self.foreverStack.pop())
            return thisIndent, "forever"

        if self.reBreak.match(statement):
            self.foreverStack.pop() # not looping so throw it away
            return self.skipIndentedStatements(newIndent)

        elif self.reContinue.match(statement):
            # go back to start of loop
            self.setLineNumber(self.foreverStack.pop())
            # we need the forever code to be reinterpreted
            #print(self.robot.getName()+"#1 FOREVER next line=", self.getLineNumber())
            return thisIndent,"forever"

        elif self.reEOF.match(statement):
            # we have reached the end of the indented statements
            # go back to the beginning of the loop
            self.setLineNumber(self.foreverStack.pop())
            #print(self.robot.getName()+" #2 FOREVER next line=",self.getLineNumber(),"statement",statement)
            # we need the forever code to be reinterpreted
            return thisIndent,"forever"

        else:
            print(self.robot.getName()+" FOREVER exit error statement=",statement)
            self.loopCount-=1
            self.setLineNumber(self.foreverStack.pop())
            return thisIndent,"forever"

    def _set(self,thisIndent,statement):
        """
        expression should be like var=,expression>
        :param thisIndent:
        :param expression:
        :return:
        """
        p=re.compile("^\s*([a-zA-Z_]\w+)\s*=\s*(.*)$")
        r=p.match(statement)
        if r:
            varname=r.group(1)
            expr=r.group(2)
            self.globals[varname]=eval(expr,self.globals)
            return self.getIndent(self.nextInstruction())
        else:
            self.Error("Expected something of the form <var>=<expr>")

    def stop(self):
        self.running=False
        self.machineControl.stop()
        t0=time.time()
        # flag is set by background tasks when they terminate
        while not self.terminated:
            # timeout waiting for 'terminated' from any background thread
            # if no threads are running this times out
            if time.time()-t0>0.1: break

    def run(self):
        """
        Run's the robot script in a seperate thread

        No return till the script ends or is terminated by stop()

        :return:
        """
        print(self.robot.getName()+" Lex.run() begins")
        self.robot.script.restart()
        self.machineControl.run()
        indent=0
        self.running=True
        self.terminated=False   # used to tell when the script has stopped

        instruction=self.nextInstruction()
        while (not self.reEOF.match(instruction)) and self.running:
            indent,instruction=self.Statement(indent,instruction)

        print(self.robot.getName()+" Lex: Script has terminated with instruction ",instruction)
        self.terminated=True
        self.machineControl.stop()