""" The serial namespace.

Library extensions should not modify this file.

"""
# Add any serial packages visible in PYHONPATH to the module path.
import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)
