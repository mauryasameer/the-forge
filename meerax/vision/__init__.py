from importlib import import_module
from typing import Any

__all__ = ["get_device", "ImageFolderDataset", "normalize", "denormalize", "plot_translation_grid"]

# Lazy (PEP 562): importing this package must not force torch/torchvision to load,
# since numpy/TensorFlow-only callers only ever need meerax.vision.gridplot.
_EXPORTS = {
    "get_device": "meerax.vision.device",
    "ImageFolderDataset": "meerax.vision.dataset",
    "normalize": "meerax.vision.dataset",
    "denormalize": "meerax.vision.dataset",
    "plot_translation_grid": "meerax.vision.gridplot",
}


def __getattr__(name: str) -> Any:
    if name in _EXPORTS:
        return getattr(import_module(_EXPORTS[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
