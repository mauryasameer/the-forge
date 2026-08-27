from __future__ import annotations

import logging

import torch

logger = logging.getLogger(__name__)


def get_device() -> torch.device:
    """Return the best available compute device: CUDA > MPS (Metal) > CPU."""
    if torch.cuda.is_available():
        logger.info("Using CUDA device")
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        logger.info("Using MPS (Metal) device")
        return torch.device("mps")
    logger.info("Using CPU device")
    return torch.device("cpu")
