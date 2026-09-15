from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RecommenderMetrics:
    precision_at_k: float
    map_at_k: float
    k: int

    def __str__(self) -> str:
        return f"Precision@{self.k}: {self.precision_at_k:.4f}\nMAP@{self.k}: {self.map_at_k:.4f}"

    def to_dict(self) -> dict[str, float | int]:
        return {"precision_at_k": self.precision_at_k, "map_at_k": self.map_at_k, "k": self.k}


def _precision_at_k_single(recommended: list[int], relevant: set[int], k: int) -> float:
    top_k = recommended[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for item in top_k if item in relevant)
    return hits / len(top_k)


def _average_precision_single(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = recommended[:k]
    hits = 0
    precisions: list[float] = []
    for rank, item in enumerate(top_k, start=1):
        if item in relevant:
            hits += 1
            precisions.append(hits / rank)
    if not precisions:
        return 0.0
    return sum(precisions) / len(relevant)


def evaluate_recommender(
    recommended: list[list[int]],
    relevant: list[set[int]],
    k: int,
) -> RecommenderMetrics:
    """Precision@K and MAP@K averaged across multiple users' recommendation lists.

    Args:
        recommended: one ranked list of recommended item ids per user (longer lists are
            truncated to the first k).
        relevant: one set of ground-truth relevant item ids per user, same order/length
            as `recommended`.
        k: cutoff rank.
    """
    if len(recommended) != len(relevant):
        raise ValueError(
            f"recommended and relevant must have the same length, got {len(recommended)} and {len(relevant)}"
        )
    if not recommended:
        return RecommenderMetrics(precision_at_k=0.0, map_at_k=0.0, k=k)

    precisions = [_precision_at_k_single(rec, rel, k) for rec, rel in zip(recommended, relevant, strict=True)]
    average_precisions = [
        _average_precision_single(rec, rel, k) for rec, rel in zip(recommended, relevant, strict=True)
    ]

    return RecommenderMetrics(
        precision_at_k=sum(precisions) / len(precisions),
        map_at_k=sum(average_precisions) / len(average_precisions),
        k=k,
    )
