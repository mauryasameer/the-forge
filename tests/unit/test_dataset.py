import pytest
import torch
from PIL import Image

from meerax.vision.dataset import ImageFolderDataset, denormalize, normalize


def _make_image(path, color=(255, 0, 0), size=(8, 8)):
    Image.new("RGB", size, color).save(path)


def test_normalize_maps_black_and_white_to_minus1_and_1():
    black = Image.new("RGB", (4, 4), (0, 0, 0))
    white = Image.new("RGB", (4, 4), (255, 255, 255))
    assert torch.allclose(normalize(black), torch.full((3, 4, 4), -1.0), atol=1e-2)
    assert torch.allclose(normalize(white), torch.full((3, 4, 4), 1.0), atol=1e-2)


def test_denormalize_is_inverse_of_normalize():
    image = Image.new("RGB", (4, 4), (128, 64, 200))
    tensor = normalize(image)
    restored = denormalize(tensor)
    assert restored.min() >= 0.0
    assert restored.max() <= 1.0


def test_dataset_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        ImageFolderDataset(tmp_path / "does-not-exist")


def test_dataset_empty_directory_raises(tmp_path):
    with pytest.raises(ValueError, match="No images found"):
        ImageFolderDataset(tmp_path)


def test_dataset_loads_images_as_chw_tensors(tmp_path):
    _make_image(tmp_path / "a.jpg")
    _make_image(tmp_path / "b.png", color=(0, 255, 0))
    dataset = ImageFolderDataset(tmp_path, image_size=16)

    assert len(dataset) == 2
    tensor = dataset[0]
    assert tensor.shape == (3, 16, 16)
    assert tensor.min() >= -1.0 and tensor.max() <= 1.0
