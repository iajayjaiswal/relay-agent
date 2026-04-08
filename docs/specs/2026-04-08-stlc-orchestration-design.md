# STLC Orchestration — Design Spec

**Date:** 2026-04-08
**Status:** Approved

---

## Overview

A multi-agent STLC (Software Testing Life Cycle) orchestration system built on the Anthropic SDK. Covers all 6 STLC stages from requirement analysis through test cycle closure. Extends the existing `lead_qa_agent` pattern with additional specialized agents for each stage.

**Entry point:** Linear ticket ID + Outline doc URL
**Exit point:** GitHub PR + Allure report + Linear updated + Slack/Email notification

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API tests | REST Assured + TestNG (Java 17, Maven) |
| Frontend tests | Playwright |
| Mobile tests | Appium + Java (Android & iOS) |
| Orchestration | Python + Anthropic SDK |
| Issue tracking | Linear |
| Docs | Outline |
| Reporting | Allure |
| Notifications | Slack + Email |
| CI | GitHub Actions |

---

## Agent Architecture

### 3-Tier Model

```
┌─────────────────────────────────────────────────┐
│       STLC Orchestrator (claude-opus-4-6)        │
│        adaptive thinking · tool use             │
└────────────────┬────────────────────────────────┘
                 │ coordinates
    ┌────────────┼──────────────────────┐
    ▼            ▼                      ▼
Stage Agents             Tool Agents
(claude-sonnet-4-6)      (claude-haiku-4-5)
```

### Orchestrator (1 agent)

| Agent | Model | Role |
|-------|-------|------|
| `stlc_orchestrator` | claude-opus-4-6 + adaptive thinking | Central brain. Coordinates the full pipeline, decides when to retry, when to advance, when to escalate to user. Never does actual work — only routes and judges. |

### Stage Agents (8 agents) — claude-sonnet-4-6

| Agent | STLC Stage | Responsibility |
|-------|-----------|----------------|
| `requirements_agent` | Stage 1 | Reads fetched Linear ticket + Outline doc, extracts testable requirements, flags ambiguities |
| `test_planning_agent` | Stage 2 | Defines scope, risk areas, test types (functional/perf/mobile), estimates effort |
| `test_case_writer` | Stage 3 | Writes test cases from analyzed requirements |
| `test_case_reviewer` | Stage 3 | Reviews test cases for coverage and quality — returns APPROVED or NEEDS REWORK |
| `test_code_writer` | Stage 3 | Converts approved test cases into automation code (REST Assured / Playwright / Appium) |
| `test_code_reviewer` | Stage 3 | Reviews automation code quality — returns APPROVED or NEEDS REWORK |
| `execution_monitor` | Stage 5 | Triggers test runs, watches results, collects pass/fail output |
| `reporting_agent` | Stage 6 | Synthesizes results into closure report, decides overall pass/fail verdict |

### Tool Agents (6 agents) — claude-haiku-4-5

| Agent | Responsibility |
|-------|----------------|
| `linear_fetcher` | Pulls ticket details and linked docs from Linear |
| `outline_fetcher` | Fetches the relevant specification doc from Outline |
| `linear_issue_creator` | Creates test plan subtasks in Linear |
| `test_runner` | Routes and triggers test runs — Maven (backend), Playwright (frontend), Appium (mobile) — in parallel |
| `allure_reporter` | Generates Allure HTML report from test results |
| `linear_updater` + `notifier` | Updates Linear ticket status, sends Slack + email summary |

**Total: 15 agents**

---

## Pipeline Flow

```
INPUT: Linear ticket ID + Outline doc URL
           │
           ▼
┌─── Stage 1: Requirement Analysis ───────────────┐
│  linear_fetcher → outline_fetcher               │
│       → requirements_agent                      │
│       → if ambiguous: pause + ask user          │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─── Stage 2: Test Planning ──────────────────────┐
│  test_planning_agent                            │
│       → linear_issue_creator                    │
│         (creates subtasks in Linear)            │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─── Stage 3: Test Case Development ─────────────┐
│  test_case_writer → test_case_reviewer          │
│       → if NEEDS REWORK: retry (max 2x)         │
│  test_code_writer → test_code_reviewer          │
│       → if NEEDS REWORK: retry (max 2x)         │
│       → create PR on GitHub                     │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─── Stage 4: Environment Check ─────────────────┐
│  verify staging/prod URLs are reachable         │
│       → if down: notify + pause                 │
│       → if up: proceed                          │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─── Stage 5: Test Execution ─────────────────────┐
│  test_runner (parallel):                        │
│    ├── REST Assured  →  mvn test                │
│    ├── Playwright    →  npx playwright test      │
│    └── Appium        →  mvn test (mobile suite) │
│  execution_monitor watches and collects results │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─── Stage 6: Test Cycle Closure ────────────────┐
│  allure_reporter   → generate HTML report       │
│  reporting_agent   → write closure summary      │
│  linear_updater    → update ticket status       │
│  notifier          → Slack + Email              │
└─────────────────────────────────────────────────┘
           │
           ▼
OUTPUT: PR link + Allure report + Linear updated + Team notified
```

---

## Orchestrator Rules

- Max 2 retries per stage before escalating to user
- Stages 3–6 only run if Stage 1 produces unambiguous requirements
- Stage 5 runs REST Assured, Playwright, and Appium in parallel
- Stage 6 always runs regardless of test outcome — failure is a valid closure
- Orchestrator uses adaptive thinking for all routing decisions

---

## File Structure

```
orchestrator-agent/
├── orchestrator.py          # STLC orchestrator (entry point)
├── agents/
│   ├── requirements.py      # Stage 1 agent
│   ├── test_planning.py     # Stage 2 agent
│   ├── test_cases.py        # Stage 3 — writer + reviewer
│   ├── test_code.py         # Stage 3 — code writer + reviewer
│   ├── execution.py         # Stage 5 — runner + monitor
│   └── reporting.py         # Stage 6 — reporting + closure
├── tools/
│   ├── linear.py            # linear_fetcher, linear_issue_creator, linear_updater
│   ├── outline.py           # outline_fetcher
│   ├── runner.py            # test_runner (maven/playwright/appium)
│   ├── allure.py            # allure_reporter
│   └── notifier.py          # slack + email notifications
├── github_pr.py             # PR creation (reused from lead_qa_agent)
├── models.py                # PipelineState dataclass
├── main.py                  # CLI entry point
├── requirements.txt
└── docs/
    └── specs/
        └── 2026-04-08-stlc-orchestration-design.md
```

---

## PipelineState

```python
@dataclass
class PipelineState:
    # Input
    linear_ticket_id: str
    outline_doc_url: str
    feature_name: str

    # Stage outputs
    raw_requirements: str = ""
    analyzed_requirements: str = ""
    test_plan: str = ""
    linear_subtask_ids: list = field(default_factory=list)
    test_cases: str = ""
    test_cases_review: str = ""
    test_code: str = ""
    test_code_review: str = ""
    pr_url: str = ""
    execution_results: dict = field(default_factory=dict)
    allure_report_path: str = ""
    closure_report: str = ""

    # Control
    tech_stack: str = "REST Assured + Playwright + Appium"
    output_dir: str = "./stlc_output"
    repo_path: str | None = None
```

---

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Ambiguous requirements | Pause pipeline, surface to user, wait for clarification |
| Agent returns NEEDS REWORK | Retry with feedback, max 2 attempts |
| Max retries exceeded | Escalate to user with context |
| Test environment unreachable | Notify team, pause Stage 5 |
| Test execution failure | Continue to Stage 6 — failure is reportable |
| Linear/Outline API error | Retry once, then surface error |

---

## Out of Scope

- SDLC stages (code writing, architecture, deployment)
- Manual test case tracking
- Real-time test monitoring dashboards
- Multi-project orchestration
