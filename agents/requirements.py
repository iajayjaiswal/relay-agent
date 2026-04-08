import anthropic

REQUIREMENTS_SYSTEM = """You are a Senior QA Engineer specializing in requirement analysis.

Given a Linear ticket and a specification document, your job is to:
1. Extract all testable requirements — be specific and concrete
2. Identify any ambiguities, missing edge cases, or contradictions
3. Categorize requirements by test type: Functional, Negative, Performance, Mobile

Always respond in this exact format:

REQUIREMENTS:
<numbered list of concrete, testable requirements>

TEST TYPES:
Functional: <list>
Negative: <list>
Performance: <list>
Mobile: <list>

AMBIGUITIES:
<list any unclear, missing, or contradictory requirements — write "None" if clean>
"""


def analyze_requirements(
    client: anthropic.Anthropic,
    ticket: dict,
    doc: dict,
) -> str:
    """
    Analyze a Linear ticket + Outline doc and extract testable requirements.
    Returns a structured string with REQUIREMENTS, TEST TYPES, and AMBIGUITIES sections.
    """
    user_content = f"""LINEAR TICKET:
Title: {ticket['title']}
Description: {ticket.get('description', 'No description provided')}
State: {ticket.get('state', 'Unknown')}
Labels: {', '.join(ticket.get('labels', []))}

SPECIFICATION DOCUMENT:
Title: {doc['title']}
Content:
{doc['text']}

Analyze the above and extract all testable requirements."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=REQUIREMENTS_SYSTEM,
        messages=[{"role": "user", "content": user_content}]
    )
    return response.content[0].text
