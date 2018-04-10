class Error(Exception):
    """base class for PixelBot exceptions"""
    pass

class RobotColorConflict(Error):
    """ Robots must all be different colors"""
    pass

class ArenaTooSmall(Error):
    """ arena is less than 100 pixels in width or height."""
    pass

class ToDo(Error):
    """ work to do """
    pass

class MissingParameters(Error):
    """ expected some parameters that were not given"""
    pass

class InvalidColor(Error):
    """ colorname is not in the list in Colors.py"""
    pass

class IndentationError(Error):
    """script indent was expected after one of IF,WHILE or FOREVER but not found"""
    pass

class InvalidAngle(Error):
    """ Invalid angle"""
    pass