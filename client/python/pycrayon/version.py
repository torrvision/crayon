r"""
Little utility to reveal the package version.
Place in the root dir of the package.
"""
from pkg_resources import get_distribution


__version__ = get_distribution(__name__.split('.')[0]).version
