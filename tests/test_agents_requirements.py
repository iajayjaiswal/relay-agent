from unittest.mock import MagicMock
from tests.conftest import make_text_response
from agents.requirements import analyze_requirements


def test_analyze_requirements_returns_structured_output(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "REQUIREMENTS:\n1. API must accept base64 image\n2. Return IFSC code\n\nAMBIGUITIES: None"
    )
    result = analyze_requirements(
        mock_anthropic_client,
        ticket={"title": "OCR Cheque", "description": "Build cheque OCR tests"},
        doc={"title": "Cheque Spec", "text": "## Overview\nAPI accepts base64..."}
    )
    assert "REQUIREMENTS" in result
    assert "base64" in result


def test_analyze_requirements_flags_ambiguity(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "REQUIREMENTS:\n1. Test all flows\n\nAMBIGUITIES:\n- 'all flows' is undefined — which flows?"
    )
    result = analyze_requirements(
        mock_anthropic_client,
        ticket={"title": "Vague ticket", "description": "Test all flows"},
        doc={"title": "No doc", "text": ""}
    )
    assert "AMBIGUITIES" in result
    assert "undefined" in result
