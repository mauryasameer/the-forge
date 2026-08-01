import torch

from forge.vision.device import get_device


def test_prefers_cuda_when_available(mocker):
    mocker.patch("torch.cuda.is_available", return_value=True)
    mocker.patch("torch.backends.mps.is_available", return_value=True)
    assert get_device() == torch.device("cuda")


def test_prefers_mps_when_cuda_unavailable(mocker):
    mocker.patch("torch.cuda.is_available", return_value=False)
    mocker.patch("torch.backends.mps.is_available", return_value=True)
    assert get_device() == torch.device("mps")


def test_falls_back_to_cpu(mocker):
    mocker.patch("torch.cuda.is_available", return_value=False)
    mocker.patch("torch.backends.mps.is_available", return_value=False)
    assert get_device() == torch.device("cpu")
