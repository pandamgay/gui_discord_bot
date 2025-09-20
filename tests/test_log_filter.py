import logging

from utils import (
    log_filter as lf,
    my_logger as ml,
    path_helper as ph
)


def test_log_filter():
    test_logger = ml.MyLogger(False, "./logs")
    test_logger = test_logger.initLogger("TestLogger")
    ml.MyLogger(True, "./logs").initLogger("Logger")

    for i in range(5):
        test_logger.debug(f"Debug log {i}")
        test_logger.info(f"Info log {i}")
        test_logger.warning(f"Warning log {i}")
        test_logger.error(f"Error log {i}")
        test_logger.debug("Additional debug log for multiline\nThis is the second line.\nAnd this is the third line.")

    path = ph.find_dir("tests") / "logs"

    debug_log = lf.log_filter(logging.DEBUG, "tests.test_log_filter", path)
    info_log = lf.log_filter(logging.INFO, "tests.test_log_filter", path)
    warning_log = lf.log_filter(logging.WARNING, "tests.test_log_filter", path)
    error_log = lf.log_filter(logging.ERROR, "tests.test_log_filter", path)

    assert "[DEBUG]" in debug_log
    assert "[INFO]" in info_log
    assert "[WARNING]" in warning_log
    assert "[ERROR]" in error_log