import anthropic
from tools.runner import RunResult

EXECUTION_SYSTEM = """You are a QA Execution Monitor.

Given raw test execution output from multiple suites, produce a clean execution summary.

Format:
EXECUTION SUMMARY:
REST Assured: <X passed / Y total>
Playwright: <X passed / Y total>
Appium: <X passed / Y total>

FAILURES:
<list any failing test names or error messages>

OVERALL: PASS / PARTIAL PASS / FAIL
"""


def monitor_execution(client: anthropic.Anthropic, run_results: dict[str, RunResult]) -> str:
    """Summarize parallel test execution results into a structured report."""
    combined_output = ""
    for suite_name, result in run_results.items():
        combined_output += f"\n--- {suite_name.upper()} (exit code: {result.returncode}) ---\n"
        combined_output += result.output[:3000]  # truncate very long logs

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=EXECUTION_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Summarize these test execution results:\n{combined_output}"
        }]
    )
    return response.content[0].text
