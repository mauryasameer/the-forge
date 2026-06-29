"""
kv_cache_benchmark.py
Benchmarks multi-head attention with and without KV caching at GPT-2 Medium scale.
Measures real speedup across token counts and saves a chart to kv_cache_speedup.png.

Requirements: numpy, matplotlib
Run:          python kv_cache_benchmark.py
"""

import time
import numpy as np
import matplotlib.pyplot as plt

# GPT-2 Medium architecture
N_HEADS  = 16
D_MODEL  = 1024
D_HEAD   = D_MODEL // N_HEADS  # 64
N_LAYERS = 24
N_TRIALS = 3

TOKEN_COUNTS = [32, 64, 128, 256, 512, 1024]

rng = np.random.default_rng(42)


def time_no_cache(seq_len: int) -> float:
    """One generation step without KV cache: recompute Q, K, V for the full sequence."""
    times = []
    for _ in range(N_TRIALS):
        t0 = time.perf_counter()
        for _ in range(N_LAYERS):
            X  = rng.standard_normal((seq_len, D_MODEL)).astype(np.float32)
            Wq = rng.standard_normal((D_MODEL, D_MODEL)).astype(np.float32)
            Wk = rng.standard_normal((D_MODEL, D_MODEL)).astype(np.float32)
            Wv = rng.standard_normal((D_MODEL, D_MODEL)).astype(np.float32)

            Q = (X @ Wq).reshape(seq_len, N_HEADS, D_HEAD).transpose(1, 0, 2)
            K = (X @ Wk).reshape(seq_len, N_HEADS, D_HEAD).transpose(1, 0, 2)
            V = (X @ Wv).reshape(seq_len, N_HEADS, D_HEAD).transpose(1, 0, 2)

            scale  = D_HEAD ** -0.5
            scores = (Q @ K.transpose(0, 2, 1)) * scale
            attn   = np.exp(scores - scores.max(-1, keepdims=True))
            attn  /= attn.sum(-1, keepdims=True)
            _      = attn @ V
        times.append(time.perf_counter() - t0)
    return float(np.median(times))


def time_with_cache(seq_len: int) -> float:
    """One generation step with KV cache: compute only for the new token, attend over full cache."""
    times = []
    for _ in range(N_TRIALS):
        # Simulate cache already holding (seq_len - 1) tokens
        k_cache = rng.standard_normal((N_LAYERS, N_HEADS, seq_len - 1, D_HEAD)).astype(np.float32)
        v_cache = rng.standard_normal((N_LAYERS, N_HEADS, seq_len - 1, D_HEAD)).astype(np.float32)

        t0 = time.perf_counter()
        for layer in range(N_LAYERS):
            x_new = rng.standard_normal((1, D_MODEL)).astype(np.float32)
            Wq    = rng.standard_normal((D_MODEL, D_MODEL)).astype(np.float32)
            Wk    = rng.standard_normal((D_MODEL, D_MODEL)).astype(np.float32)
            Wv    = rng.standard_normal((D_MODEL, D_MODEL)).astype(np.float32)

            q     = (x_new @ Wq).reshape(N_HEADS, 1, D_HEAD)
            k_new = (x_new @ Wk).reshape(N_HEADS, 1, D_HEAD)
            v_new = (x_new @ Wv).reshape(N_HEADS, 1, D_HEAD)

            K = np.concatenate([k_cache[layer], k_new], axis=1)   # (H, seq_len, d)
            V = np.concatenate([v_cache[layer], v_new], axis=1)

            scale  = D_HEAD ** -0.5
            scores = (q @ K.transpose(0, 2, 1)) * scale            # (H, 1, seq_len)
            attn   = np.exp(scores - scores.max(-1, keepdims=True))
            attn  /= attn.sum(-1, keepdims=True)
            _      = attn @ V                                       # (H, 1, d)
        times.append(time.perf_counter() - t0)
    return float(np.median(times))


def main() -> None:
    print(f"GPT-2 Medium — {N_LAYERS} layers · {N_HEADS} heads · d_model={D_MODEL}\n")
    print(f"{'Tokens':>8}  {'No Cache (ms)':>14}  {'KV Cache (ms)':>14}  {'Speedup':>9}")
    print("─" * 52)

    no_cache_ms, cache_ms, speedups = [], [], []

    for seq_len in TOKEN_COUNTS:
        t_no  = time_no_cache(seq_len)  * 1000
        t_kv  = time_with_cache(seq_len) * 1000
        sx    = t_no / t_kv
        no_cache_ms.append(t_no)
        cache_ms.append(t_kv)
        speedups.append(sx)
        print(f"{seq_len:>8}  {t_no:>14.1f}  {t_kv:>14.1f}  {sx:>8.2f}×")

    # ── Chart ──────────────────────────────────────────────────────────────
    BG, GRID, TEXT_DIM = '#0f1117', '#2a2a2a', '#a09994'

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor(BG)

    for ax in (ax1, ax2):
        ax.set_facecolor(BG)
        ax.tick_params(colors=TEXT_DIM)
        ax.xaxis.label.set_color(TEXT_DIM)
        ax.yaxis.label.set_color(TEXT_DIM)
        ax.title.set_color('#e8e4dc')
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID)

    ax1.plot(TOKEN_COUNTS, no_cache_ms, 'o-', color='#c8a96e', label='No cache',  linewidth=2, markersize=6)
    ax1.plot(TOKEN_COUNTS, cache_ms,    's-', color='#00e5cc', label='KV cache',  linewidth=2, markersize=6)
    ax1.set_xlabel('Sequence length (tokens)')
    ax1.set_ylabel('Time per step (ms)')
    ax1.set_title('Latency: KV Cache vs No Cache')
    ax1.legend(facecolor='#1a1a1a', labelcolor='#e8e4dc', edgecolor=GRID)

    bar_width = [t * 0.6 for t in TOKEN_COUNTS]
    ax2.bar(TOKEN_COUNTS, speedups, color='#F59E0B', width=bar_width)
    ax2.axhline(1, color='#6b6460', linestyle='--', linewidth=1)
    ax2.set_xlabel('Sequence length (tokens)')
    ax2.set_ylabel('Speedup (×)')
    ax2.set_title('KV Cache Speedup Factor')

    plt.tight_layout(pad=2)
    out = 'kv_cache_speedup.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor=BG)
    print(f'\nChart saved → {out}')


if __name__ == '__main__':
    main()
