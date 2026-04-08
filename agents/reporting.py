import anthropic

REPORTING_SYSTEM = """You are a QA Lead writing the Test Cycle Closure Report.

Given the execution summary, test plan, and feature name, produce a professional closure report.

Format:
CLOSURE REPORT:
Feature: <name>
Date: <today>
Test Plan Scope: <from test plan>

RESULTS:
Total Test Cases: <count>
Passed: <count>
Failed: <count>
Blocked: <count>

VERDICT: PASS / CONDITIONAL PASS / FAIL
NOTES: <key observations, known issues, risks>
"""


def write_closure_report(
    client: anthropic.Anthropic,
    feature_name: str,
    execution_summary: str,
    test_plan: str,
) -> str:
    """Write the final STLC closure report with a pass/fail verdict."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=REPORTING_SYSTEM,
        messages=[{
            "role": "user",
            "content": (
                f"Feature: {feature_name}\n\n"
                f"TEST PLAN:\n{test_plan}\n\n"
                f"EXECUTION SUMMARY:\n{execution_summary}\n\n"
                "Write the closure report."
            )
        }]
    )
    return response.content[0].text
