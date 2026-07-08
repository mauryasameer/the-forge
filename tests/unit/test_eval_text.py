from forge.eval.text import bleu_score, rouge_l


def test_rouge_l_perfect():
    assert rouge_l("the cat sat on the mat", "the cat sat on the mat") == 1.0


def test_rouge_l_empty():
    assert rouge_l("", "something") == 0.0
    assert rouge_l("something", "") == 0.0


def test_rouge_l_partial():
    score = rouge_l("the cat sat", "the dog sat")
    assert 0.0 < score < 1.0


def test_bleu_identical():
    refs = ["the cat sat on the mat"]
    hyps = ["the cat sat on the mat"]
    score = bleu_score(refs, hyps)
    assert score > 0.9


def test_bleu_empty_hypothesis():
    refs = ["the cat sat on the mat"]
    hyps = [""]
    score = bleu_score(refs, hyps)
    assert score == 0.0
