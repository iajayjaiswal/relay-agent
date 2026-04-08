# STLC Orchestrator Agent

A multi-agent STLC (Software Testing Life Cycle) orchestration system built on the Anthropic SDK.

## Overview

Automates all 6 STLC stages using 15 specialized Claude agents:

1. **Requirement Analysis** — Pulls from Linear + Outline docs
2. **Test Planning** — Creates Linear subtasks
3. **Test Case Development** — Writes, reviews, and codes test cases → GitHub PR
4. **Environment Check** — Verifies staging/prod is reachable
5. **Test Execution** — Runs REST Assured, Playwright, and Appium in parallel
6. **Test Cycle Closure** — Allure report + Linear update + Slack/Email

## Design

See [`docs/specs/2026-04-08-stlc-orchestration-design.md`](docs/specs/2026-04-08-stlc-orchestration-design.md)

## Agent Model

| Tier | Model | Count |
|------|-------|-------|
| Orchestrator | claude-opus-4-6 + adaptive thinking | 1 |
| Stage agents | claude-sonnet-4-6 | 8 |
| Tool agents | claude-haiku-4-5 | 6 |

## Usage

```bash
python main.py --ticket LINEAR-123 --outline-url https://your-outline-doc
```
