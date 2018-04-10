"""

"""
print("PIXELBOT SIMULATOR STARTING - PLEASE WAIT")
import time
t0=time.clock()
from tkinter import *
from Forms import ScriptManager
t1=time.clock()
print("Main imports took %.6fs"%(t1-t0))


ARENA=(800,800)
CONSOLE=(600,150)
MANAGER=(600,800)
FPS=50


sm=ScriptManager.ScriptManager(parent=Tk(),size=MANAGER,arena=ARENA,consoleSize=CONSOLE ,fps=FPS,
                               robotConfig="robot.json")
sm.show() # no return till program is stopped
