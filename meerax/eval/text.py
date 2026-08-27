from __future__ import annotations


def bleu_score(
    references: list[list[str] | str],
    hypotheses: list[str],
    max_n: int = 4,
) -> float:
    """Corpus-level BLEU-{max_n} score using NLTK's smoothed implementation.

    Args:
        references:  One reference per hypothesis (string or pre-tokenised list).
        hypotheses:  Generated texts to evaluate.
        max_n:       Maximum n-gram order (default 4 → BLEU-4).
    """
    from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu

    refs = [[r.split() if isinstance(r, str) else r] for r in references]
    hyps = [h.split() if isinstance(h, str) else h for h in hypotheses]
    weights = tuple(1.0 / max_n for _ in range(max_n))
    return float(corpus_bleu(refs, hyps, weights=weights, smoothing_function=SmoothingFunction().method1))


def rouge_l(reference: str, hypothesis: str) -> float:
    """ROUGE-L F1 score using Longest Common Subsequence (no external deps)."""
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()
    if not ref_tokens or not hyp_tokens:
        return 0.0
    m, n = len(ref_tokens), len(hyp_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = (
                dp[i - 1][j - 1] + 1
                if ref_tokens[i - 1] == hyp_tokens[j - 1]
                else max(dp[i - 1][j], dp[i][j - 1])
            )
    lcs = dp[m][n]
    precision = lcs / n if n else 0.0
    recall = lcs / m if m else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
