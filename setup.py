""" Setup script for the serial-core library.

"""
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


_CONFIG = {
    "name": "serial-core",
    "author": "Michael Klatt",
    "author_email": "mdklatt@alumni.ou.edu",
    "url": "https://github.com/mdklatt/serial-python",
    "package_dir": {"": "src"},
    "packages": find_packages("src")
}


def version():
    """ Get the local package version.

    """
    file = Path("src", "serial", "core", "__version__.py")
    namespace = {}
    exec(file.read_text(), namespace)
    return namespace["__version__"]


def main():
    """ Execute the setup commands.

    """
    setup(version=version(), **_CONFIG)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
