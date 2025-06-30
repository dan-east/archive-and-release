class ProjectError(Exception):
    """
    Base class for all raised by this project.
    Using this as a base class for all custom errors allows developers to use except ProjectException to trap these project-based custom exceptions.
    """

    
class UtilityError(ProjectError) :
    """Raised by utility functions."""
    




class ZipError(UtilityError) :
    """Raised by the zip utility functions to indicate some issue."""


class FileError(UtilityError) :
    """Raised by the file utility functions to indicate some issue."""
    
    

