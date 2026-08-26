from importlib import import_module
from typing import Any

__all__ = ["get_device", "ImageFolderDataset", "normalize", "denormalize", "plot_translation_grid"]

# Lazy (PEP 562): importing this package must not force torch/torchvision to load,
# since numpy/TensorFlow-only callers only ever need forge.vision.gridplot.
_EXPORTS = {
    "get_device": "forge.vision.device",
    "ImageFolderDataset": "forge.vision.dataset",
    "normalize": "forge.vision.dataset",
    "denormalize": "forge.vision.dataset",
    "plot_translation_grid": "forge.vision.gridplot",
}


def __getattr__(name: str) -> Any:
    if name in _EXPORTS:
        return getattr(import_module(_EXPORTS[name]), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
