from importlib.metadata import version

from meerax.logging import setup_logger

__version__ = version("meerax")

__all__ = ["setup_logger", "__version__"]
