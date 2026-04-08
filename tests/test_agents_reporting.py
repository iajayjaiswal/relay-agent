from tests.conftest import make_text_response
from agents.reporting import write_closure_report


def test_write_closure_report_returns_verdict(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "CLOSURE REPORT:\nFeature: OCR Cheque\nVERDICT: PASS\nTotal: 70, Passed: 65, Failed: 5"
    )
    result = write_closure_report(
        mock_anthropic_client,
        feature_name="OCR Cheque",
        execution_summary="REST Assured: 45/48...",
        test_plan="Scope: Functional, Negative"
    )
    assert "VERDICT" in result
    assert "CLOSURE REPORT" in result
