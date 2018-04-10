"""
simple line class

used in collision calculations

"""

import math

class Line():
    """
    convert bot direction and current XY to a line formula so we can use it to calculate
    collision paths

    y=mx+c
    """
    slope=0
    c=0

    def __init__(self,direction,x,y):
        self.slope=math.tan(math.radians(direction))
        divisor=self.slope*float(x)
        try:
            self.c=y/divisor
        except Exception as e:
            print("Line.__init__() Division by zero slope=",self.slope,"x=",x)