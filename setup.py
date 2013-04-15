""" Distutils setup script for the datalect library.

For basic installation in the current user's site-packages directory:
    python setup.py install --user

"""
from distutils.core import setup
from sys import exit

from datalect.core import __version__


def main():
    config = {
        "name": "datalect",
        "version": __version__,
        "packages": ("datalect", "datalect.core", "datalect.core.serial"),
        "author": "Michael Klatt",
        "author_email": "mdklatt@ou.edu"}
    setup(**config)
    return 0


if __name__ == "__main__":
    exit(main())
