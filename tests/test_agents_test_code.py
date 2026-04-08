from tests.conftest import make_text_response
from agents.test_code import write_test_code, review_test_code


def test_write_test_code_generates_java_for_rest_assured(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "@Test\npublic void testOCRChequeValidResponse() {\n  // REST Assured test\n}"
    )
    result = write_test_code(
        mock_anthropic_client,
        test_cases="TC-001: Valid cheque returns 200",
        tech_stack="REST Assured + TestNG"
    )
    assert "@Test" in result


def test_write_test_code_generates_playwright_for_frontend(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "test('upload cheque', async ({ page }) => {\n  await page.goto('/upload');\n});"
    )
    result = write_test_code(
        mock_anthropic_client,
        test_cases="TC-010: Upload cheque via UI",
        tech_stack="Playwright"
    )
    assert "page" in result


def test_review_test_code_returns_approved(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "VERDICT: APPROVED\nCode quality is good."
    )
    result = review_test_code(mock_anthropic_client, test_code="@Test\npublic void test() {}")
    assert "APPROVED" in result


def test_review_test_code_returns_needs_rework(mock_anthropic_client):
    mock_anthropic_client.messages.create.return_value = make_text_response(
        "VERDICT: NEEDS REWORK\nFEEDBACK: No assertions present in test methods."
    )
    result = review_test_code(mock_anthropic_client, test_code="@Test\npublic void test() { // TODO }")
    assert "NEEDS REWORK" in result
