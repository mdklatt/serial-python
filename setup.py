""" Distutils setup script for the serial.core library package.

Basic command to run the test suite and install in the user's package directory
if all tests pass:

    python setup.py test install --user

"""
from distutils.core import Command
from distutils.core import setup
from subprocess import check_call
from tempfile import TemporaryFile

from serial.core import __version__
from test import run as run_tests

SETUP_CONFIG = {
    "name": "serial-core",
    "packages": ("serial", "serial.core"),
    "author": "Michael Klatt",
    "author_email": "mdklatt@ou.edu",
    "version": __version__}


class TestCommand(Command):
    """ Custom setup command to run the test suite.
    
    """
    description = "run the test suite"
    user_options = []
    
    def initialize_options(self):
        """ Set the default values for all options this command supports.
        
        """
        return
        
    def finalize_options(self):
        """ Set final values for all options this command supports.
        
        This is run after all other option assigments have been completed (e.g.
        command-line options, other commands, etc.)
        
        """
        return

    def run(self):
        """ Execute the command.
        
        """
        if run_tests() != 0:
            raise RuntimeError("test suite failed")
        return


class UpdateCommand(Command):
    """ Custom setup command to update from the tracking branch.
    
    """
    description = "update from the tracking branch"
    user_options = [
        ("remote=", "r", "remote name [default: tracking remote]"),
        ("branch=", "b", "branch name [default: tracking branch]")]
    
    def initialize_options(self):
        """ Set the default values for all options this command supports.
        
        """
        # By default, use the remote tracking branch.
        self.remote = ""
        self.branch = ""
        return
        
    def finalize_options(self):
        """ Set final values for all options this command supports.
        
        This is run after all other option assigments have been completed (e.g.
        command-line options, other commands, etc.)
        
        """
        return

    def run(self):
        """ Execute the command.
        
        """
        args = {"remote": self.remote, "branch": self.branch}
        cmdl = "git pull --ff-only {remote:s} {branch:s}".format(**args)
        check_call(cmdl.split())  # throws exception on error
        return


# class Git(object):
#     """ Basic git interface.
#     
#     """
#     
#     
#     def _exec(self, cmd, *args):
#         """ Execute a git command.
#         
#         The return value is the output send to stdout. If the command returns
#         with an error a CalledProcessError exception is raised.
#         
#         """
        
    

    

def main():
    """ Execute the setup commands.
    
    """
    SETUP_CONFIG["cmdclass"] = {"test": TestCommand, "update": UpdateCommand}
    setup(**SETUP_CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
