from tests.conftest import make_text_response
from agents.test_cases import write_test_cases, review_test_cases


def test_write_test_cases_returns_formatted_cases(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "TC-001: Valid cheque image returns 200 with IFSC\nTC-002: Invalid base64 returns 400"
    )
    result = write_test_cases(mock_anthropic_client, requirements="REQUIREMENTS:\n1. Accept base64 image")
    assert "TC-001" in result
    assert "TC-002" in result


def test_review_returns_approved(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "VERDICT: APPROVED\nCoverage is complete."
    )
    result = review_test_cases(
        mock_anthropic_client,
        test_cases="TC-001: ...\nTC-002: ...",
        requirements="REQUIREMENTS:\n1. ..."
    )
    assert "APPROVED" in result


def test_review_returns_needs_rework(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "VERDICT: NEEDS REWORK\nFEEDBACK: Missing negative test for empty image field."
    )
    result = review_test_cases(
        mock_anthropic_client,
        test_cases="TC-001: Only happy path",
        requirements="REQUIREMENTS:\n1. Accept base64\n2. Reject empty input"
    )
    assert "NEEDS REWORK" in result
    assert "FEEDBACK" in result
