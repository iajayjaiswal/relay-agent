from unittest.mock import patch, MagicMock
from models import PipelineState
from orchestrator import build_tools, execute_tool


def test_build_tools_returns_all_stage_tools():
    tools = build_tools()
    tool_names = [t["name"] for t in tools]
    assert "fetch_linear_ticket" in tool_names
    assert "fetch_outline_doc" in tool_names
    assert "analyze_requirements" in tool_names
    assert "write_test_plan" in tool_names
    assert "create_linear_subtasks" in tool_names
    assert "write_test_cases" in tool_names
    assert "review_test_cases" in tool_names
    assert "write_test_code" in tool_names
    assert "review_test_code" in tool_names
    assert "run_tests" in tool_names
    assert "monitor_execution" in tool_names
    assert "generate_allure_report" in tool_names
    assert "write_closure_report" in tool_names
    assert "update_linear_ticket" in tool_names
    assert "notify_team" in tool_names


def test_execute_tool_fetch_linear_ticket(mock_anthropic_client):
    state = PipelineState(
        linear_ticket_id="QA-123",
        outline_doc_url="https://outline.test/doc/abc",
        feature_name="OCR Cheque"
    )
    with patch("orchestrator.linear.fetch_ticket", return_value={
        "id": "abc", "title": "OCR Cheque", "description": "Test it", "state": "In Progress", "labels": []
    }) as mock_fetch:
        result = execute_tool(mock_anthropic_client, "fetch_linear_ticket", {}, state)
        mock_fetch.assert_called_once_with("QA-123")
        assert state.raw_requirements != "" or "OCR Cheque" in result
