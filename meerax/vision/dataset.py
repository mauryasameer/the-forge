from __future__ import annotations

import logging
from pathlib import Path

import torch
import torchvision.transforms.functional as TF
from PIL import Image
from torch.utils.data import Dataset

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def normalize(image: Image.Image) -> torch.Tensor:
    """Convert a PIL RGB image to a (3, H, W) float tensor in [-1, 1]."""
    tensor = TF.to_tensor(image.convert("RGB"))  # [0, 1]
    result: torch.Tensor = tensor * 2.0 - 1.0
    return result


def denormalize(tensor: torch.Tensor) -> torch.Tensor:
    """Inverse of `normalize`: a [-1, 1] tensor back to [0, 1], same shape."""
    return ((tensor + 1.0) / 2.0).clamp(0.0, 1.0)


class ImageFolderDataset(Dataset[torch.Tensor]):
    """Loads every image in a flat directory as a normalized (3, image_size, image_size) tensor."""

    def __init__(self, directory: str | Path, image_size: int = 256) -> None:
        self.directory = Path(directory)
        if not self.directory.exists():
            raise FileNotFoundError(f"Image directory not found: {self.directory}")
        self.image_size = image_size
        self.paths = sorted(
            p for p in self.directory.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS
        )
        if not self.paths:
            raise ValueError(f"No images found in {self.directory}")
        logger.info("Loaded %d images from %s", len(self.paths), self.directory)

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, idx: int) -> torch.Tensor:
        image = Image.open(self.paths[idx]).resize(
            (self.image_size, self.image_size), Image.Resampling.BICUBIC
        )
        return normalize(image)
