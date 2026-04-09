import json
import anthropic

LOCATOR_MODEL = "claude-haiku-4-5-20251001"


def extract_relevant_locators(
    client: anthropic.Anthropic,
    raw_locators: list[dict],
    requirements: str,
) -> str:
    """Uses claude-haiku to filter locators relevant to the feature requirements."""
    response = client.messages.create(
        model=LOCATOR_MODEL,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""You are given UI element locators extracted from an Android app and feature requirements to test.

Select only the locators relevant to the requirements and format them as a locator map for Appium test automation.

Requirements:
{requirements}

Extracted locators:
{json.dumps(raw_locators, indent=2)}

Output format:
```
LOCATOR MAP
===========
Screen: <screen name>
  <element name>:
    resource-id: <value>
    content-desc: <value>
    class: <value>
```

Only include locators relevant to the requirements. Group by screen.""",
            }
        ],
    )
    return response.content[0].text
