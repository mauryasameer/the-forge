import logging

from meerax.logging import setup_logger


def test_returns_logger():
    logger = setup_logger("meerax.test.logging")
    assert isinstance(logger, logging.Logger)


def test_idempotent():
    a = setup_logger("meerax.test.idempotent")
    b = setup_logger("meerax.test.idempotent")
    assert a is b
    assert len(a.handlers) == 1


def test_level_default():
    logger = setup_logger("meerax.test.level")
    assert logger.level == logging.INFO


def test_custom_level():
    logger = setup_logger("meerax.test.debug", level=logging.DEBUG)
    assert logger.level == logging.DEBUG
