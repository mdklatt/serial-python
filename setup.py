""" Setup script for the serial-core library.

"""
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


_config = {
    "name": "serial-core",
    "author": "Michael Klatt",
    "author_email": "mdklatt@alumni.ou.edu",
    "url": "https://github.com/mdklatt/serial-python",
    "package_dir": {"": "src"},
    "packages": find_packages("src")
}


def main():
    """ Execute the setup command.

    """
    def version():
        """ Get the local package version. """
        namespace = {}
        path = Path("src", "serial", "core", "__version__.py")
        exec(path.read_text(), namespace)
        return namespace["__version__"]

    _config.update({
        "version": version(),
    })
    setup(**_config)
    return 0


# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
