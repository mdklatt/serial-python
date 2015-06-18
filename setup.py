""" Distutils setup script for the serial.core library package.

Basic command to run the test suite and install in the user's package directory
if all tests pass:

    python setup.py test install --user

"""
from setuptools import Command
from setuptools import setup
from distutils import log
from subprocess import check_call
from subprocess import CalledProcessError

from test import run as run_tests


_CONFIG = {
    "name": "serial-core",
    "packages": ("serial", "serial.core"),
    "author": "Michael Klatt",
    "author_email": "mdklatt@alumni.ou.edu",
    "url": "https://github.com/mdklatt/serial-python"
}


def version():
    """ Return the local package version.

    """
    with open("serial/core/__version__.py") as stream:
        exec(stream.read())
    return __version__


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

        This is run after all other option assignments have been completed
        (e.g. command-line options, other commands, etc.)

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
        log.info("package version is {0:s}".format(version()))
        if run_tests() != 0:
            raise SystemExit(1)
        return


class UpdateCommand(_CustomCommand):
    """ Custom setup command to pull from a remote branch.

    """
    description = "update from the tracking branch"
    user_options = [
        ("remote=", "r", "remote name [default: tracking remote]"),
        ("branch=", "b", "branch name [default: tracking branch]"),
    ]

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
        try:
            check_call(cmdl.split())
        except CalledProcessError:
            raise SystemExit(1)
        log.info("package version is now {0:s}".format(version()))
        return


class VirtualenvCommand(_CustomCommand):
    """ Custom setup command to create a virtualenv environment.

    """
    description = "create a virtualenv environment"
    user_options = [
        ("name=", "m", "environment name [default: venv]"),
        ("python=", "p", "Python interpreter"),
        ("requirements=", "r", "pip requirements file"),
    ]

    def initialize_options(self):
        """ Set the default values for all user options.

        """
        self.name = "venv"
        self.python = None  # default to version used to install virtualenv
        self.requirements = None
        return

    def run(self):
        """ Execute the command.

        """
        venv = "virtualenv {0:s}"
        if self.python:
            venv += " -p {1:s}"
        pip = "{0:s}/bin/pip install -r {2:s}" if self.requirements else None
        args = self.name, self.python, self.requirements
        try:
            check_call(venv.format(*args).split())
            if pip:
                log.info("installing requirements")
                check_call(pip.format(*args).split())
        except CalledProcessError:
            raise SystemExit(1)
        return


def main():
    """ Execute the setup commands.

    """
    _CONFIG["version"] = version()
    _CONFIG["cmdclass"] = {
        "test": TestCommand,
        "update": UpdateCommand,
        "virtualenv": VirtualenvCommand
    }
    setup(**_CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
