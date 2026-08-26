# gridplot numpy/TF support

## Problem

`forge.vision.gridplot.plot_translation_grid` only accepts `torch.Tensor` images
(`(3, H, W)` in `[-1, 1]`), via a hard `.permute(1, 2, 0).detach().cpu().numpy()` call. This
blocks any TensorFlow/Keras-based project (e.g. `style_gan`, a CycleGAN retrofit currently being
brainstormed) from using it, since TF tensors don't have `.permute()`/`.detach()` and TF images
are channels-last `(H, W, C)` by convention, not channels-first like PyTorch.

## Goals

- `plot_translation_grid` accepts `torch.Tensor | np.ndarray` per row.
- No new dependency — forge does not learn about TensorFlow specifically. A TF caller converts
  via the framework's own `.numpy()` (available in eager mode) before calling; forge only ever
  sees `np.ndarray`.
- Grayscale images (`(H, W, 1)` or `(H, W)`) render correctly via `imshow`, matching the
  single-channel case `style_gan`'s CycleGAN actually needs.

## Non-goals

- Accepting channels-first numpy arrays. Numpy/TF/PIL's native convention is channels-last;
  nothing in the current or anticipated caller set produces channels-first numpy images. Adding
  that branch now would be speculative.
- Any change to `forge.vision.dataset` (the PyTorch `ImageFolderDataset`) — untouched, still
  torch-only, unrelated to this fix.

## Design

Add a private dispatch helper in `forge/vision/gridplot.py`:

```python
def _to_display_array(image: torch.Tensor | np.ndarray) -> np.ndarray:
    if isinstance(image, torch.Tensor):
        return denormalize(image).permute(1, 2, 0).detach().cpu().numpy()
    array = np.clip((np.asarray(image, dtype=np.float32) + 1.0) / 2.0, 0.0, 1.0)
    if array.ndim == 3 and array.shape[-1] == 1:
        array = array[..., 0]
    return array
```

`plot_translation_grid`'s loop body calls `_to_display_array(tensor)` instead of the current
inline `denormalize(tensor).permute(1, 2, 0).detach().cpu().numpy()`, and its signature/docstring
update to `rows: list[tuple[str, torch.Tensor | np.ndarray]]`, documenting both accepted shapes
and conventions (torch: channels-first `(3,H,W)`; numpy: channels-last `(H,W,C)` or `(H,W)`).

## Testing

`tests/unit/test_gridplot.py` gains numpy-path cases alongside the existing torch-path tests:
- A 3-channel numpy `(H, W, 3)` array in `[-1, 1]` renders without error, output image data in
  `[0, 1]`.
- A single-channel numpy `(H, W, 1)` array squeezes correctly to `(H, W)` for `imshow`.
- Mixed rows (one torch tensor, one numpy array) in the same call still work.
- Existing torch-only tests continue to pass unmodified — this is a strictly additive change.

## Versioning

MINOR bump: `0.3.0` → `0.4.0` (new capability, fully backward compatible — no existing caller's
behavior changes).
