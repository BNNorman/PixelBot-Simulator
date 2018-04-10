"""
Movement.py

Generally useful routine to move a bot along a line or curve

"""
import math
from Constants import *
from Exceptions import *

def linearMove(robot,dist):
    curX, curY = robot.getPos()
    direction = robot.getDirection()
    newX = curX+dist * math.cos(direction)
    newY = curY+dist * math.sin(direction)
    robot.setPos((newX, newY))

def getWheelSpeed(diameter,rps):
    """
    Given the wheel diameter and revs per second
    calculate the linear speed

    :param int diameter: wheel diameter
    :param int rps: revolutions per second
    :return float speed:
    """
    circ=math.pi*diameter
    return rps*circ

def getWheelRpsNeeded(distance, time,wheelDia):
    """
    calculates and return the rps of the wheel required
    to travel the given distance in the required time.
    :param int distance: mm to travel
    :param float time: number of seconds to take
    :param int wheelDia: mm diameter
    :return:
    """
    rotations=distance/(math.pi*wheelDia)
    return rotations/time

def hMotion(robot):
    """
    return horizontal motion as LEFT or RIGHT
    :param robot:
    :return: LEFT,RIGHT,UNDECIDED
    """
    # conversion to degrees makes the following easier to read
    direction=int(math.degrees(robot.getDirection())) %360

    if 90 <= direction <= 270:    return LEFT

    # there is discontinuous range heading right
    if 90 >= direction >= 0:     return RIGHT
    if 360>= direction >=270:       return RIGHT


    return UNDECIDED

def vMotion(robot):
    # conversion to degrees makes the following easier to read
    direction=int(math.degrees(robot.getDirection())) % 360

    if 180>=direction>=0:     return DOWN
    if 180<=direction<=360:   return UP

    if direction==90:       return DOWN
    if direction==270:      return UP

    return UNDECIDED

def arcCentre(rx,ry,radius,direction):
    """
    Calculate the centre of rotation for an arc of given radius
    with robot at rx,ry travelling in direction (radians)

    +ve radius means turning right, negative is left

    Calculation is affected by direction of motions

    :param float x: robot X
    :param float y: robot Y
    :param int or float radius: arc radius
    :param float direction: radians - the current direction of the robot
    :return:
    """

    # easier to visualise with degrees
    # pygame draws clockwise from the usual zero position
    dirDegrees=math.degrees(direction) % 360

    if (180<=dirDegrees<=270):
        ang = math.radians(360 - (dirDegrees + 90))
        if radius>0:
            cx = rx + abs(radius) * math.cos(ang)
            cy = ry - abs(radius) * math.sin(ang)
        else:
            cx = rx - abs(radius) * math.cos(ang)
            cy = ry + abs(radius) * math.sin(ang)

    elif (270<=dirDegrees<=360):
        ang=math.radians(dirDegrees+90-360)
        if radius > 0:
            cx = rx + abs(radius) * math.cos(ang)
            cy = ry + abs(radius) * math.sin(ang)
        else:
            cx = rx - abs(radius) * math.cos(ang)
            cy = ry - abs(radius) * math.sin(ang)

    elif (0 <= dirDegrees <= 90):

        ang=math.radians(180-(dirDegrees+90))
        if radius > 0:
            cx = rx - abs(radius) * math.cos(ang)
            cy = ry + abs(radius) * math.sin(ang)
        else:
            cx = rx + abs(radius) * math.cos(ang)
            cy = ry - abs(radius) * math.sin(ang)

    elif (90 <= dirDegrees <= 180):
        ang=math.radians(dirDegrees-90)
        if radius > 0:
            cx = rx - abs(radius) * math.cos(ang)
            cy = ry - abs(radius) * math.sin(ang)
        else:
            cx = rx + abs(radius) * math.cos(ang)
            cy = ry + abs(radius) * math.sin(ang)

    else:
        raise InvalidAngle("Unable to fit angle in 0-360 range - got "+str(dirDegrees))

    return int(cx),int(cy)

def anglePoint(x,y,cx,cy):
    """
    given a centre and a point on the circle calculate the
    angle

    EAST is zero, angles measure anti-clockwise to match PyGame

    :param int or float x0: x coord of point on circumference of circle
    :param int or float y0: y coord
    :param int or float cx: circle centre X
    :param int or float cy: circle centre Y
    :return angle: in degrees
    """

    at2=math.atan2(cy - y, cx - x)
    ang = math.degrees(math.atan2(cy - y, cx - x))

    # atans2 appears to return angles where WEST=0
    return 180+ang

def rotatePoint(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python

    The angle should be given in radians.

    :param tuple origin: (cx,cy)
    :param tuple point: (x,y)
    :param float or int angle: radians + is clockwise -ve is anti clockwise
    :return:
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    #print("rotatePoint cx,cy",ox,oy,"px,py",px,py,"angle,",angle,"qx,qy",qx,qy)
    return qx, qy

def within(x,y,rect):
    """

    returns true if x/y lies within the rectangle

    :param float or int x: point coord
    :param float or int y: point coord
    :param tuple rect: area (x,y,w,h)
    :return:
    """
    ax,ay,aw,ah=rect

    if x>=ax and x<=aw and y>=ay and y<=ah:
        return True
    return False

