# Language Reference

The PixelBot simulator script interpreter implements MOST of the PixelBot language. Notably it doesn't implement star
commands.

The language is evolving with use.

You should look at the [HullOS specification ](https://github.com/HullPixelbot/HullOS) first.

## Interpreter

The simulator interprets the PixelBot control scripts on a line by line basis. The code is not compiled or tokenised 
since the execution is rarely time critical.

Each PixelBot interprets its control script in separate python threads. This allows PixelBots to run independently of
 each other.

### Code Blocks

Like python, the HullOS utilises code indentation to signify code blocks. Indeed, HullOS is intended to be a 
precursor for students moving onto python.

In the HullOS specification there is provision for using BEGIN-END keywords to signfiy the start and end of blocks of
 code. These are NOT required in this emulator/simulator BUT if they are used the interpreter expects the lines 
 between BEGIN and END to be indented.
 
### Comments

Source code may be commented using #. All text following a # is ignored.

### Blank lines

Blank lines in source code are permitted and ignored.

### Sample script

    POS 100 200     # position the PixelBot at X=100 y=200 in the arena
    ANGLE 0         # facing East - note angles are 0-360 anti-clockwise
    FOREVER
        MOVE 100 INTIME 10  # move 100 steps (pixels) in 10 tenths of a second (1 second)
        TURN 90             # instantly turn clockwise 90 degrees
        
In the simulator the script is not case sensitive - it could be written in lowercase or mixed case.
   
Using BEGIN-END to denote code blocks the script could also be written like this (comments removed for sinmplicity):-
    
    BEGIN
        POS 100 200 
        ANGLE 0 
        FOREVER
            BEGIN
                MOVE 100 INTIME 10
                TURN 90
            END
    END
   
## Expressions

In the HullOS specification the expressions are quite simple by design but in the simulator we use the python 
**eval** statement which means that expressions can be a complex as python allows. You need to avoid using 
expressions which a PixelBot cannot evaluate - so keep them simple.


### Defining Variables

syntax:-
    SET VARNAME=<expression>
    
You can declare any variable name provided it conforms to the normal naming convention of a leading underscore or 
letter followed by a mixture of letters, numbers or underscores.

<expression> may include variable names (which must be declared before first use)

### System Variables
    
As per the HullOS specification the following special variables provide information which can be used in expressions.
 Note ALL system variables return hardware information and are preceeded with an @ character

None of these are case sensitive:-

@DISTANCE   - returns the current ultrasound sensor reading.
@RANGE      - not in the HullOS specification but suggestion put forward. Returns the max distance sensor range
@LIGHT      - returns the light level detected by a light sensor above the robots. Currently this returns 
@ANGLE      - returns the direction the robot is facing using 0-360 anti-clockwise
@COMPASS    - returns the direction of the robot using nautical compass values 0-360 where 0=NORYN
@X          - current X coordinate of the robot
@Y          - current Y coordinate of the robot
@NAME       - name of the robot
@RANDOM     - returns a random number in range 1-12
@MOVING     - returns True if the robot is moving

## Robot Control

### MOVE
syntax:-

    MOVE <dist> [ INTIME <time> [ BACKGROUND]]
    
<dist> is the number of pixels you want the robot to move forward. Negative distances move the robot in reverse. The 
motion is instantaneous (a hyperjump) unless the INTIME clause is used.

The <time> parameter sets the number of tenths of a second that the motion will take place in. So MOVE 100 INTIME 10 
moves the robot 100 pixels in 1 second.

If BACKGROUND is specified the script will continue to the next instruction and leave the motion taking place in a 
separate thread. Otherwise, the script interpretation stops till the motion is finished.

### TURN
Syntax:-

    TURN <angle> [ INTIME <<time> [ BACKGROUND]]
    
<angle> is in degrees clockwise. Negative values are anti-clockwise. The turn is instantaneous unless INTIME is 
specified. The robot rotates about it's physical centre.

The <time> parameter sets the number of tenths of a second that the motion will take place in. So TURN 90 INTIME 100 
turns the robot right 90 degrees in 10 seconds.

If BACKGROUND is specified the script will continue to the next instruction and leave the motion taking place in a 
separate thread. Otherwise, the script interpretation stops till the motion is finished.

### ARC
Syntax:

    ARC <radius> ANGLE <degrees> [ INTIME <time> [BACKGROUND]]

This causes the robot to move along an arc.

<radius> is the radius of rotation 90 degrees right from the current XY position of the robot. A positive value 
causes a motion to the right wheras negative values cause a motion to the left.

<degrees> the angle to turn through. Athe abs() value of <angle> is used because <radius> determines the direction.

The motion is instantaneous (which makes no sense - may as well use POS and ANGLE) unless INTIME is specified.
    
The <time> parameter sets the number of tenths of a second that the motion will take place in.

If BACKGROUND is specified the script will continue to the next instruction and leave the motion taking place in a 
separate thread. Otherwise, the script interpretation stops till the motion is finished.

### ANGRY

Syntax:-
    ANGRY
    
The PixelBot has a ring of LEDs on the top. ANGRY causes them to flash RED.

### HAPPY

Syntax:-
    HAPPY
    
The PixelBot has a ring of LEDs on the top. ANGRY causes them to flash GREEN.

### DELAY
Syntax:-
    DELAY <time>

Delays execution of the robot script for <time> tenths of a second.

### POS
Syntax:-
    POS <x> <y>
    
Sets the robiots current coordinates - a hyperjump if you like

### DIR
Syntax:-
    DIR <angle>
 
Makes the robot face the direction <angle. which is measured anti-clockwise from East.   
    
### ANGLE

Syntax:-
    ANGLE <degrees>
    
An alias for DIR

### COMPASS
Syntax:-
    COMPASS <angle>

Makes the robot face <angle> measured clockwise from North


### COLOR
Syntax:-
    COLOR RED|GREEN|BLUE|MAGENTA|YELLOW|CYAN|BLACK|WHITE
    
Changes the body color of the robot - could get confusing.

### PRINT
Syntax:-
    PRINT <expression>
    
Allows the robot to print messages to the console. Print does not output a linefeed but the output is prepended with 
the robot name (which doesn't happen with a real PixelBot but is essential when several bots are chattering in the 
simulator)

### PRINTLN
Syntax:-
    PRINTLN <expression>
    
As with PRINT but this does add a linefeed to the end of the output. Since the expression evaluation in the simulator
 is better than a real PixelBot this is to be preferred over PRINT for clarity of output.
    
### SOUND
Syntax:-
    SOUND <freq> <time> [ WAIT]
    
Uses the pygame sound mixer to output square wave notes. The real PixelBot generates sound by switching a digital 
line on/off hence the use of square waves.

<fre> is the frequency of the note.
<time> is the number of milliseconds the note should sound for

If WAIT is specified the interpreter waits till the note has finished sounding before going to the next instruction, 
which may be another note. Remember, the robot will stop moving till the note has finished sounding.

The PyGame mixer used by the simulator has 8 channels. It automatically selects a non-busy channel to produce the sound.
 If you don't use WAIT all your notes may play simultaneously.
     
## Program Flow Control

The language provides IF-ELSE, FOREVER and WHILE for flow control. IF and WHILE evaluate conditional expressions 
which resolve to True or False as per the standard python way of doing things.


### FOREVER

Forever declares a block of code which will execute forever unless a BREAK instruction is executed.

A CONTINUE instruction will cause execution to resume at the code line immediately following the FOREVER instruction.

Syntax:-

    FOREVER
        <indented statements>


### IF-ELSE

IF-ELSE statements are available in every language.

Else is an optional clause.

Syntax:-

    IF <CONDITION>
        <indented code>
    ELSE
        <indented code>


### WHILE

WHILE executes a code block as long as the expression evaluates to True.

Syntax:-

    WHILE <condition>
        <indented statements>

BREAK and CONTINUE work in the same way as for FOREVER

    
## Collisions

Collision avoidance is built into the simulator.

If a robot centre coordinates are WALLMARGIN (defined in Constants.py) pixels from the arena wall the path of the 
robot is reflected which is like bouncing off the wall.

If a robot collides with another they both adjust their tracks by 45 defgrees to the right. With the real PixelBot 
this doesn't happen - collisions can halt the robots.


