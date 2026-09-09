"""Turns the eval file's pass/fail counts into a score, and gates on a rate."""

import os

EVAL_FILE = "test_evals.py"
MIN_PASS_RATE = float(os.environ.get("EVAL_MIN_PASS_RATE", "0.80"))

_results: dict[str, str] = {}


def pytest_runtest_logreport(report):
    if report.when == "call" and EVAL_FILE in report.nodeid:
        _results[report.nodeid] = report.outcome


def _rate() -> tuple[int, int, float]:
    passed = sum(1 for o in _results.values() if o == "passed")
    total = len(_results)
    return passed, total, (passed / total if total else 1.0)


def pytest_terminal_summary(terminalreporter):
    passed, total, rate = _rate()
    if not total:
        return
    terminalreporter.write_sep("=", "eval score")
    terminalreporter.write_line(
        f"{passed}/{total} questions pass  ({rate:.0%}, threshold {MIN_PASS_RATE:.0%})"
    )


def pytest_sessionfinish(session, exitstatus):
    passed, total, rate = _rate()
    if not total:
        return
    other_failures = session.testsfailed - (total - passed)
    if other_failures == 0 and rate >= MIN_PASS_RATE:
        session.exitstatus = 0
