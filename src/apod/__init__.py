''' init dot pie '''
from importlib.metadata import version, PackageNotFoundError

try:
    from ._version import version as __version__
    from ._version import version_tuple
except PackageNotFoundError:
    __version__ = 'unknown version'
