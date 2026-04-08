from unittest.mock import patch, MagicMock
from tools.runner import RunResult
from agents.execution import monitor_execution
from tests.conftest import make_text_response


def test_monitor_execution_summarises_results(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "EXECUTION SUMMARY:\nREST Assured: 45/48 passed\nPlaywright: 12/12 passed\nAppium: 8/10 passed\nOVERALL: PARTIAL PASS"
    )
    run_results = {
        "rest_assured": RunResult("rest_assured", True, "Tests run: 48, Failures: 3", 1),
        "playwright": RunResult("playwright", True, "passed 12", 0),
        "appium": RunResult("appium", False, "Tests run: 10, Failures: 2", 1),
    }
    summary = monitor_execution(mock_anthropic_client, run_results)
    assert "EXECUTION SUMMARY" in summary
    assert "OVERALL" in summary
