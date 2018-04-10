# PixelBot Simulator

Intended to be used as a means to check HullOS code before downloading to a PixelBot as produced by Rob Miles. 
Checkout [HullOS](https://github.com/HullPixelbot/HullOS) on Github.

Written in pure python the simulator uses Pygame for graphics and smartquadtree for collision detection.

Smartquadtree has the ability to mask the quadtree using a python list of vertices for the required shape. In the 
code I create a cone representing the ukltrasound sensor region of interest. Smartquadtree then returns only the 
robots which are within that area and so are potential collision candidates.

This is Windows oriented but it should be possible to run on MacOS.

## Software requirements

- python 3.5 32bit or python 2.7 32bit
- smartquadtree-1.0-py35-win32.egg or smartquadtree-1.0-py27-win32.egg
- pygame 1.92

If you want to build a win64 version of smartquadtree then you need the [sources](https://github.com/xoolive/quadtree).


- Install python as per normal then cd into the scripts folder in a command window.
- pip install smartquadtree  
If this doesn't find smartquadtree then try downloading the [egg](https://pypi.python.org/pypi/smartquadtree) then 
use easy_install <path to egg>
- pip install pygame

# Forms

This folder contains the main user forms except the PyGame window


# Files

robot.json - config data for all the robots.

# Scripts

Location of all robot scripts