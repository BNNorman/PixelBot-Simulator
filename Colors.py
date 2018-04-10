"""
colours by name
"""

from Exceptions import *

RED=0xFF00
GREEN=0x00FF00
BLUE=0x0000FF
BLACK=0x000000
WHITE=0xFFFFFF
MAGENTA=0xFF00FF
CYAN=0x00FFFF
YELLOW=0xFFFF00


colorByName={}
colorByName["RED"]=RED
colorByName["GREEN"]=GREEN
colorByName["BLUE"]=BLUE
colorByName["BLACK"]=BLACK
colorByName["WHITE"]=WHITE
colorByName["MAGENTA"]=MAGENTA
colorByName["YELLOW"]=YELLOW
colorByName["CYAN"]=CYAN

def getColorByName(name):
    name=name.upper()
    if name in colorByName: return colorByName[name]
    raise InvalidColor("I don't know that color: "+str(name))
