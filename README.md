# Relay

A 15-agent system that automates the full Software Testing Life Cycle — from Linear ticket to GitHub PR, Allure report, and team notifications.

Agents pass work to each other like a relay race: requirements → test plan → test cases → code → execution → closure.

## What It Does

Give it a Linear ticket ID and an Outline doc URL. It runs all 6 STLC stages autonomously:

| Stage | What happens |
|-------|-------------|
| 1. Requirement Analysis | Fetches ticket + doc → extracts testable requirements |
| 2. Test Planning | Writes test plan → creates Linear subtasks |
| 3. Test Case Development | Writes test cases → reviews → writes automation code → reviews → opens GitHub PR |
| 4. Environment Check | Verifies staging/prod URLs are reachable |
| 5. Test Execution | Runs REST Assured + Playwright + Appium in parallel |
| 6. Test Cycle Closure | Generates Allure report → updates Linear → sends Slack + email |

## Agent Architecture

| Tier | Model | Count | Role |
|------|-------|-------|------|
| Orchestrator | claude-opus-4-6 + adaptive thinking | 1 | Drives the pipeline via tool use, never does work itself |
| Stage agents | claude-sonnet-4-6 | 8 | Reasoning-heavy work per STLC stage |
| Tool agents | claude-haiku-4-5 | 6 | Fast I/O — Linear, Outline, runner, Allure, notifier |

## Prerequisites

- Python 3.11+
- Java 17 + Maven (for REST Assured tests)
- Node.js (for Playwright tests)
- Appium server running locally (for mobile tests)
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/iajayjaiswal/orchestrator-agent.git
cd orchestrator-agent

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
```

Open `.env` and fill in your credentials:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
LINEAR_API_KEY=lin_api_...
OUTLINE_API_KEY=...
OUTLINE_BASE_URL=https://your-outline-instance.com
GITHUB_TOKEN=ghp_...
GITHUB_REPO=owner/repo

# Slack notifications
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#qa-notifications

# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=team@yourcompany.com

# Paths to your test projects
MAVEN_PROJECT_PATH=../your-java-tests
PLAYWRIGHT_PROJECT_PATH=../your-playwright-tests
APPIUM_PROJECT_PATH=../your-mobile-tests
APPIUM_SERVER_URL=http://localhost:4723
```

## Running

```bash
python main.py
```

It will prompt you for:

```
🚀 Relay — STLC Multi-Agent Pipeline
────────────────────────────────────────
Linear ticket ID (e.g. QA-123): QA-123
Outline doc URL: https://your-outline.com/doc/your-spec
Feature name (e.g. OCR Cheque): OCR Cheque Processing
Tech stack [REST Assured + Playwright + Appium]:
Output dir [./stlc_output]:
```

Or pass arguments directly:

```bash
python main.py \
  --ticket QA-123 \
  --outline-url "https://your-outline.com/doc/your-spec" \
  --feature "OCR Cheque Processing"
```

## Output

```
✅ Done. PR: https://github.com/your-org/your-repo/pull/42
📊 Allure: ./stlc_output/target/site/allure-maven-plugin
📋 Closure: All 47 test cases passed across REST Assured, Playwright, and Appium suites...
```

## Running Tests

```bash
pytest tests/ -v --tb=short
```

All 25 tests should pass. No real API calls are made — everything is mocked.

## Project Structure

```
orchestrator-agent/
├── orchestrator.py        # Central orchestrator — 15 tool definitions + agentic loop
├── main.py                # Interactive CLI entry point
├── models.py              # PipelineState dataclass
├── github_pr.py           # GitHub PR creation
├── agents/
│   ├── requirements.py    # Stage 1: requirement analysis
│   ├── test_planning.py   # Stage 2: test planning
│   ├── test_cases.py      # Stage 3a: test case writer + reviewer
│   ├── test_code.py       # Stage 3b: test code writer + reviewer
│   ├── execution.py       # Stage 5: execution monitor
│   └── reporting.py       # Stage 6: closure report
├── tools/
│   ├── linear.py          # Linear API — fetch, create subtasks, update status
│   ├── outline.py         # Outline API — fetch docs
│   ├── runner.py          # Parallel test runner (Maven / Playwright / Appium)
│   ├── allure.py          # Allure report generator
│   └── notifier.py        # Slack + email notifications
├── tests/                 # 25 tests, all passing
├── requirements.txt
├── .env.example
└── docs/
    └── specs/
        └── 2026-04-08-stlc-orchestration-design.md
```

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Ambiguous requirements | Pipeline pauses, surfaces to user |
| Agent returns NEEDS REWORK | Retries with feedback, max 2 attempts |
| Max retries exceeded | Escalates to user with context |
| Test environment unreachable | Notifies team, pauses Stage 5 |
| Test execution failure | Continues to Stage 6 — failure is reportable |
| Linear/Outline API error | Retries once, then surfaces error |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | Python + Anthropic SDK |
| Backend tests | REST Assured + TestNG (Java 17, Maven) |
| Frontend tests | Playwright |
| Mobile tests | Appium + Java |
| Issue tracking | Linear |
| Docs | Outline |
| Reporting | Allure |
| Notifications | Slack + Email |
