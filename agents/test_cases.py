import anthropic

WRITER_SYSTEM = """You are a Senior QA Engineer writing test cases.

For each requirement, write test cases covering:
- Happy path (valid inputs, expected success)
- Negative cases (invalid inputs, edge cases, boundary values)
- Error scenarios (missing fields, wrong types, auth failures)

Format each test case as:
TC-XXX | <Test Name> | <Precondition> | <Steps> | <Expected Result> | <Type: Functional/Negative/Performance/Mobile>
"""

REVIEWER_SYSTEM = """You are a QA Lead reviewing test cases for quality and coverage.

Check for:
- Complete requirement coverage (every requirement has at least one test)
- Missing negative/edge cases
- Vague or untestable steps
- Duplicate test cases
- Incorrect expected results

Always respond in this exact format:
VERDICT: APPROVED or NEEDS REWORK
FEEDBACK: <specific issues to fix, or "None" if approved>
"""


def write_test_cases(
    client: anthropic.Anthropic,
    requirements: str,
    feedback: str = ""
) -> str:
    """Write test cases from requirements. Include feedback if reworking."""
    content = requirements
    if feedback:
        content = f"FEEDBACK TO ADDRESS:\n{feedback}\n\nREQUIREMENTS:\n{requirements}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=WRITER_SYSTEM,
        messages=[{"role": "user", "content": f"Write test cases for:\n\n{content}"}]
    )
    return response.content[0].text


def review_test_cases(
    client: anthropic.Anthropic,
    test_cases: str,
    requirements: str
) -> str:
    """Review test cases against requirements. Returns APPROVED or NEEDS REWORK with feedback."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=REVIEWER_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"REQUIREMENTS:\n{requirements}\n\nTEST CASES TO REVIEW:\n{test_cases}"
        }]
    )
    return response.content[0].text
