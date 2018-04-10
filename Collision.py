"""
Collision.py

Library to support collision detection

"""
import math
from Line import *
from Robot import *
from Motion import *

def getIntersectCoords(line1,line2):
    """
    calculate where two lines will cross
    :param Line line1:
    :param Line line2:
    :return: x,y - point where the lines cross or None
    """
    if line1.slope==line2.slope: return None

    x=(line1.c-line2.c)/(line2.slope-line1.slope)
    y=line1.c+line1.slope*x
    return x,y


def getTimeToCoords(X,Y,bot):
    """
    calculate time for bot to reach XY which is obtained from intersectCoords()

    :param int X: intersect coordinate X
    :param int Y: intersect coordiante Y
    :param Robot bot: the bot to use for calculating time
    :return:
    """
    x,y=bot.getPos()
    xDiff=X-x
    yDiff=Y-y
    dist_to_travel=math.sqrt(xDiff*xDiff+yDiff*yDiff)
    speed=bot.getSpeed()
    if speed>0: return dist_to_travel/speed
    else: return dist_to_travel/0.001

def haveCollided(botA,botB):
    """
    work out if botA and botB have collided

    collision is true if the line between centres < 2xradius

    :param botA: first bot
    :param botB: nearest bot
    :return:  True or False
    """
    xa,ya=botA.getPos()
    xb,yb=botB.getPos()

    xDiff=abs(xa-xb)
    yDiff=abs(ya-yb)

    sep=math.sqrt(xDiff*xDiff+yDiff*yDiff)

    # robots are the same size
    if sep<2*botA.getSize():
        print("Bot ",botA.getName()," has collided with",botB.getName())
        return True
    elif sep > 0.1*2 * botA.getSize():
        print("No collision but close call!")
        return False
    else:
        print("No collision, not even close")
        return False



def willCollide(botA,botB):
    """

    :param Quadtree botA: pointer to bot
    :param Quadtree botB: pointer to bot
    :return bool: True if will collide, False otherwise
    """

    line1=Line(botA.direction,botA.get_x(),botA.get_y())
    line2=Line(botB.direction,botB.get_x(),botB.get_y())

    X,Y=getIntersectCoords(line1,line2)

    t1=getTimeToCoords(X,Y,botA)
    t2=getTimeToCoords(X,Y,botB)

    if t1==t2:
        print("Bot ",botA.getName()," will collide with",botB.getName(),"at",X,Y,"in %.2fs"%(float(t1)))
        return True
    elif (abs(t1-t2)/t1)<0.1:
        print("No collision but close call")
        return False
    else:
        print("No collision, not even close")
        return False



def checkWallBump(robot):
    """
    check if robot is approaching the arena walls

    Returns a tuple:-
        bump        True or False
        hMovement   LEFT or RIGHT
        vMovement   UP or DOWN

    Should be called from the robot mover routine to allow it to take evasive action.

    :param PixelBot robot:
    :return tuple: Bump,hMovement,vMovement
    """
    # canvas is rectangular
    width,height=robot.arena
    bump = False

    robotX,robotY=robot.getPos()

    nearestDist=WALLMARGIN+(robot.getSize()/2)
    #prevDir=robot.getDirection() # radians

    hMovement=hMotion(robot)
    vMovement=vMotion(robot)

    if (robotX <= nearestDist) and (hMovement == LEFT):
        bump = True

    elif (robotX >= (width - nearestDist)) and (hMovement == RIGHT):
        bump = True

    if (robotY <= nearestDist) and (vMovement == UP):
        bump = True

    elif (robotY >= (height - nearestDist)) and (vMovement == DOWN):
        bump = True

    # mover routine needs to take action
    return bump,hMovement,vMovement



def getWallDistance(canvas,robot):
    width,height=canvas.get_width(),canvas.get_height()

    hM=hMotion(robot)
    if hM==LEFT:
        Line1=Line(robot.getDirection,robot.get_x(),robot.get_y())
        Line2=Line(math.pi/2,0,0)
        xh,yh=getIntersectCoords(Line1,Line2)


    elif hM==RIGHT:
        Line1=Line(robot.getDirection,robot.get_x(),robot.get_y())
        Line2=Line(math.pi/2,width,height)
        xh,yh=getIntersectCoords(Line1,Line2)

    vM = vMotion(robot)
    if vM == UP:
        Line1 = Line(robot.getDirection, robot.get_x(), robot.get_y())
        Line2 = Line(0, 0, 0)
        xv, yv = getIntersectCoords(Line1, Line2)
    elif vM == DOWN:
        Line1 = Line(robot.getDirection, robot.get_x(), robot.get_y())
        Line2 = Line(0, 0, height)
        xv, yv = getIntersectCoords(Line1, Line2)



def circleAndLineIntersect(robot,line,circle):
    # line just comprises m and c
    # circle is cx/cy and radius (r)

    mSq=line.m*line.m
    A=mSq+1
    B=2*(line.m*line.c-line.m*circle.cy-circle.cx)
    C=circle.cy*circle.cy-circle.r*circle.r+circle.cx*circle.cx-2*line.c*circle.cy+line.c*line.c

    if B*B-4*A*C<0: return False
    return True


def checkArcWallBump(robot,arena,cX,cY):
    """
    robot travelling in an arc into the 'forbidden zone' needs to have the direction and centre of rotation reflected.

    returns the new direction,centre of rotation and initial turn angle for the robot

    :param robot:
    :param float or int cx: center of curved path
    :param float or int cy: center of curved path
    :return dir,newCx,newCy,turnAngle:
    """

    bump,hMove,vMove=checkWallBump(robot)
    if not bump:
        return None,0,0,0

    # calculate if collision is near top, left,right of botton

    w,h=arena
    rX,rY=robot.getPos()
    curDir=math.degrees(robot.getDirection())%360

    # work out which wall we are bumping on
    place=None

    hDirection=hMotion(robot)
    vDirection=vMotion(robot)

    # check if not moving away from walls
    if rX<=WALLMARGIN and hDirection==LEFT:
        D=2*abs(rY-cY)
        newCy = cY + D if cY < rY else cY - D
        newDir = 180 - curDir
        return math.radians(newDir % 360), cX, newCy, math.radians(anglePoint(rX, rY, cX, newCy))

    if rX>=(w-WALLMARGIN) and hDirection==RIGHT:
        D = 2 * abs(rY - cY)
        newCy = cY + D if cY < rY else cY - D
        newDir = 180 - curDir if curDir <= 90 else 540-curDir
        return math.radians(newDir % 360), cX, newCy, math.radians(anglePoint(rX, rY, cX, newCy))

    if rY<=WALLMARGIN and vDirection==UP:
        D=2*abs(rX-cX)
        newCx = cX + D if cX < rX else cX - D
        newDir = 360 - curDir
        return math.radians(newDir % 360), newCx, cY, math.radians(anglePoint(rX, rY, newCx, cY))

    if rY>=(h-WALLMARGIN) and vDirection==DOWN:
        D=2*abs(rX-cX)
        newCx = cX + D if cX < rX else cX - D
        newDir = 360 - curDir
        return math.radians(newDir % 360), newCx, cY, math.radians(anglePoint(rX, rY, newCx, cY))

    else:
        return None,0,0,0









