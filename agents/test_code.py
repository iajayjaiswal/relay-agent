import anthropic

CODE_WRITER_SYSTEM = """You are a Senior QA Automation Engineer.

Generate production-ready automation test code based on test cases and the specified tech stack:

- REST Assured + TestNG (Java): For backend API tests. Use the pattern from existing framework — extend BaseTest, use RequestBuilder, assert with ResponseValidator.
- Playwright (TypeScript): For frontend tests. Use page object model, await all actions, assert with expect().
- Appium + Java: For mobile tests. Use AppiumDriver, explicit waits, MobileBy selectors.

Write complete, runnable code. No placeholders. Include all imports.
"""

CODE_REVIEWER_SYSTEM = """You are a Senior QA Lead reviewing automation test code.

Check for:
- Assertions present and meaningful (not just status code checks)
- No hardcoded credentials or environment-specific values
- Proper use of the tech stack patterns
- No commented-out dead code
- Test methods are independent (no shared mutable state)

Always respond in this exact format:
VERDICT: APPROVED or NEEDS REWORK
FEEDBACK: <specific issues, or "None" if approved>
"""


def write_test_code(
    client: anthropic.Anthropic,
    test_cases: str,
    tech_stack: str,
    feedback: str = "",
    locator_map: str = ""
) -> str:
    """Generate automation code from test cases. Include feedback if reworking."""
    content = test_cases
    if feedback:
        content = f"FEEDBACK TO ADDRESS:\n{feedback}\n\nTEST CASES:\n{test_cases}"

    locator_section = f"Appium Locator Map (use these exact locators in your Appium code):\n{locator_map}" if locator_map else ""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=CODE_WRITER_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Tech Stack: {tech_stack}\n\nGenerate automation code for:\n\n{content}\n\n{locator_section}"
        }]
    )
    return response.content[0].text


def review_test_code(client: anthropic.Anthropic, test_code: str) -> str:
    """Review automation code. Returns APPROVED or NEEDS REWORK with feedback."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=CODE_REVIEWER_SYSTEM,
        messages=[{"role": "user", "content": f"Review this test code:\n\n{test_code}"}]
    )
    return response.content[0].text
