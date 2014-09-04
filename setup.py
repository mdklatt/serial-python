""" Distutils setup script for the serial.core library package.

Basic command to run the test suite and install in the user's package directory
if all tests pass:

    python setup.py test install --user

"""
from distutils.core import Command
from distutils.core import setup
from subprocess import call

import test  # select the correct version of unittest
from unittest import defaultTestLoader
from unittest import TextTestRunner

from serial.core import __version__


_CONFIG = {
    "name": "serial-core",
    "packages": ("serial", "serial.core"),
    "author": "Michael Klatt",
    "author_email": "mdklatt@ou.edu",
    "version": __version__}


class _CustomCommand(Command):
    """ Abstract base class for a distutils custom setup command. 
    
    """
    # Each user option is a tuple consisting of the option's long name (ending
    # with "=" if it accepts an argument), its single-character alias, and a
    # description.
    description = ""
    user_options = []  # this must be a list
    
    def initialize_options(self):
        """ Set the default values for all user options.
        
        """
        return
        
    def finalize_options(self):
        """ Set final values for all user options.
        
        This is run after all other option assigments have been completed (e.g.
        command-line options, other commands, etc.)
        
        """
        return
        
    def run(self):
        """ Execute the command.
       
        Raise SystemExit to indicate failure. 
        
        """
        raise NotImplementedError
    

class TestCommand(_CustomCommand):
    """ Custom setup command to run the test suite.
    
    """
    description = "run the test suite"

    def run(self):
        """ Execute the command.
        
        """
        suite = defaultTestLoader.discover("test", "[a-z]*.py")
        result = TextTestRunner().run(suite)
        if not result.wasSuccessful():
            raise SystemExit 
        return


class UpdateCommand(_CustomCommand):
    """ Custom setup command to pull from a remote branch.
    
    """
    description = "update from the tracking branch"
    user_options = [
        ("remote=", "r", "remote name [default: tracking remote]"),
        ("branch=", "b", "branch name [default: tracking branch]")]
    
    def initialize_options(self):
        """ Set the default values for all user options.
        
        """
        self.remote = ""  # default to tracking remote
        self.branch = ""  # default to tracking branch
        return
        
    def run(self):
        """ Execute the command.
        
        """
        args = {"remote": self.remote, "branch": self.branch}
        cmdl = "git pull --ff-only {remote:s} {branch:s}".format(**args)
        if call(cmdl.split()) != 0:
            raise SystemExit
        return


def main():
    """ Execute the setup commands.
    
    """
    setup(cmdclass={"test": TestCommand, "update": UpdateCommand}, **_CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
