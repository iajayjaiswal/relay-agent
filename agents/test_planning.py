import anthropic

TEST_PLANNING_SYSTEM = """You are a QA Lead responsible for test planning.

Given analyzed requirements, produce a structured test plan with:
1. Feature overview and scope
2. Risk areas (what's most likely to break)
3. Test types to cover (Functional, Negative, Performance, Mobile)
4. Concrete subtasks to be created in Linear

Always respond in this exact format:

TEST PLAN:
Feature: <name>
Scope: <comma-separated test types>
Risk Areas: <key risk areas>

EFFORT ESTIMATE:
Test Cases: <approximate count>
Automation Hours: <estimate>

SUBTASKS:
<numbered list — each subtask is one concrete Linear issue to create>
"""


def write_test_plan(client: anthropic.Anthropic, analyzed_requirements: str) -> str:
    """
    Produce a structured test plan from analyzed requirements.
    Returns a string with TEST PLAN and SUBTASKS sections.
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=TEST_PLANNING_SYSTEM,
        messages=[{
            "role": "user",
            "content": f"Write a test plan for the following requirements:\n\n{analyzed_requirements}"
        }]
    )
    return response.content[0].text
