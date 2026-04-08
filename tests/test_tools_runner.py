import pytest
from unittest.mock import patch, MagicMock
from tools.runner import run_all_tests, RunResult


def make_completed_process(returncode, stdout, stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


def test_run_all_tests_returns_results_for_all_three_suites():
    with patch("tools.runner.subprocess.run") as mock_run:
        mock_run.return_value = make_completed_process(0, "BUILD SUCCESS\nTests run: 5, Failures: 0")
        results = run_all_tests()

    assert "rest_assured" in results
    assert "playwright" in results
    assert "appium" in results


def test_run_all_tests_marks_failed_suite():
    def side_effect(cmd, **kwargs):
        if "mvn" in cmd:
            return make_completed_process(1, "BUILD FAILURE\nTests run: 3, Failures: 2")
        return make_completed_process(0, "passed 10")

    with patch("tools.runner.subprocess.run", side_effect=side_effect):
        results = run_all_tests()

    assert results["rest_assured"].passed is False
    assert results["playwright"].passed is True


def test_run_result_dataclass():
    r = RunResult(suite="rest_assured", passed=True, output="Tests run: 5", returncode=0)
    assert r.suite == "rest_assured"
    assert r.passed is True
