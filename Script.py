"""
Script.py

Simple class to upload a script and retrieve lines of the script

Handles retrieving of script commands.


"""

import time
import re
from Constants import *


class Script():

    theScript=None
    lastInstruction=None
    lineNumber=0

    # pattern used to exclude comments
    p = re.compile(r"^\s*(.*)#.*$")

    def __init__(self,aScript=None):

        if aScript is not None:
            self.theScript=aScript
            self.restart()
        else:
            self.script=[]


    def uploadScript(self, fname):
        try:
            f = open(fname,"r")
            theScript=f.readlines()
            f.close()

            # lex deals with comment lines by ignoring them
            # we just remove the trailing newline (if it exists)
            self.theScript=[]
            for line in range(len(theScript)):
                self.theScript.append(theScript[line].rstrip())

            self.restart()
            return True, "Ok"

        except Exception as e:
            print("Script.uploadScript() exception",e.args)
            return False, "Unable to load script "+fname+" are you sure the path is correct?"

    def replaceScript(self,theScript=None):
        """
        used to replace the text of the script on the fly
        :param theScript: list of instructions
        :return: nothing
        """
        self.theScript=theScript
        self.restart()

    def getNextInstruction(self):
        self.lineNumber+=1

        if self.theScript is None:
            print("Script.getNextInstruction() theScript is None")
            return EOF
        if self.lineNumber>=len(self.theScript):
            #print("Script.getNextInstruction() step beyond end of script")
            return EOF

        line=self.theScript[self.lineNumber]

        # if it begings with # it's a comment so fetch next line
        m=self.p.match(line)

        if m:
            # if the whole line was a comment
            if len(m.group(1))==0: return self.getNextInstruction()
            # the comment was at the end of the line
            self.lastInstruction=m.group(1)
            return m.group(1)
        # no comments on this line
        self.lastInstruction=line

        return line

    def getLastInstruction(self):
        assert self.lastInstruction is not None,"Call to getLastInstruction() before getNextInstruction()."
        return self.lastInstruction

    def getLineNumber(self):
        return self.lineNumber

    # used by looping commands FOREVER, and WHILE
    def setLineNumber(self,lineNo):
        self.lineNumber=lineNo

    def restart(self):
        self.lastInstruction=None
        self.lineNumber=-1
