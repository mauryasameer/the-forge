import pytest

from meerax.eval.recommender import evaluate_recommender


def test_perfect_precision():
    recommended = [[1, 2, 3]]
    relevant = [{1, 2, 3}]
    m = evaluate_recommender(recommended, relevant, k=3)
    assert m.precision_at_k == pytest.approx(1.0)
    assert m.map_at_k == pytest.approx(1.0)
    assert m.k == 3


def test_zero_precision_no_overlap():
    recommended = [[1, 2, 3]]
    relevant = [{4, 5, 6}]
    m = evaluate_recommender(recommended, relevant, k=3)
    assert m.precision_at_k == pytest.approx(0.0)
    assert m.map_at_k == pytest.approx(0.0)


def test_partial_precision_and_rank_sensitive_map():
    # user 1: hits at rank 1 and 3 out of top-3 -> precision 2/3
    # AP = (1/1 + 2/3) / 2 relevant items = 0.8333...
    recommended = [[1, 9, 2]]
    relevant = [{1, 2}]
    m = evaluate_recommender(recommended, relevant, k=3)
    assert m.precision_at_k == pytest.approx(2 / 3)
    assert m.map_at_k == pytest.approx((1 / 1 + 2 / 3) / 2)


def test_averages_across_multiple_users():
    recommended = [[1, 2, 3], [4, 5, 6]]
    relevant = [{1, 2, 3}, {7, 8, 9}]
    m = evaluate_recommender(recommended, relevant, k=3)
    assert m.precision_at_k == pytest.approx((1.0 + 0.0) / 2)


def test_truncates_recommended_list_to_k():
    recommended = [[1, 2, 3, 4, 5]]
    relevant = [{4, 5}]
    m = evaluate_recommender(recommended, relevant, k=3)
    assert m.precision_at_k == pytest.approx(0.0)  # 4,5 are outside top-3


def test_to_dict_keys():
    m = evaluate_recommender([[1]], [{1}], k=1)
    d = m.to_dict()
    assert set(d.keys()) == {"precision_at_k", "map_at_k", "k"}


def test_mismatched_list_lengths_raises():
    with pytest.raises(ValueError):
        evaluate_recommender([[1, 2]], [{1}, {2}], k=1)
