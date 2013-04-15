""" Distutils setup script for the serial.core library package.

For basic installation in the current user's site-packages directory:
    python setup.py install --user

"""
from distutils.core import setup
from sys import exit

from serial.core import __version__


def main():
    config = {
        "name": "serial-core",
        "version": __version__,
        "packages": ("serial", "serial.core"),
        "author": "Michael Klatt",
        "author_email": "mdklatt@ou.edu"}
    setup(**config)
    return 0


if __name__ == "__main__":
    exit(main())
