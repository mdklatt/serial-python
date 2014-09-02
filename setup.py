""" Distutils setup script for the serial.core library package.

Basic command to run the test suite and install in the user's package directory
if all tests pass:

    python setup.py test install --user

"""
from distutils.core import Command
from distutils.core import setup
from subprocess import check_call

from serial.core import __version__
from tests._unittest import defaultTestLoader 
from tests._unittest import TextTestRunner 


CONFIG = {
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
        
        """
        raise NotImplementedError
    

class TestCommand(_CustomCommand):
    """ Custom setup command to run the test suite.
    
    """
    description = "run the test suite"

    def run(self):
        """ Execute the command.
        
        """
        suite = defaultTestLoader.discover("tests", "*_test.py")
        TextTestRunner().run(suite)
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
        check_call(cmdl.split())  # throws exception on error
        return


def main():
    """ Execute the setup commands.
    
    """
    setup(cmdclass={"test": TestCommand, "update": UpdateCommand}, **CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
