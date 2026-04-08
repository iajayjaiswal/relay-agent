from tests.conftest import make_text_response
from agents.test_planning import write_test_plan


def test_write_test_plan_returns_plan_with_subtasks(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        """TEST PLAN:
Feature: OCR Cheque
Scope: Functional, Negative, Mobile
Risk Areas: Base64 encoding, IFSC lookup

SUBTASKS:
1. Write functional test cases for OCR Cheque happy path
2. Write negative test cases for invalid inputs
3. Write mobile Appium test cases
4. Write automation code for all test cases
5. Execute tests and generate Allure report"""
    )
    result = write_test_plan(mock_anthropic_client, analyzed_requirements="REQUIREMENTS:\n1. Accept base64...")
    assert "SUBTASKS" in result
    assert "Risk Areas" in result


def test_write_test_plan_includes_all_test_types(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "TEST PLAN:\nScope: Functional, Negative, Performance, Mobile\nSUBTASKS:\n1. Functional tests"
    )
    result = write_test_plan(mock_anthropic_client, analyzed_requirements="REQUIREMENTS:\n1. Test API")
    assert "Functional" in result
