# orchestrator.py
import json
import anthropic
from rich.console import Console
from rich.panel import Panel

import tools.linear as linear
import tools.outline as outline
import tools.runner as runner
import tools.allure as allure
import tools.notifier as notifier
import agents.requirements as req_agent
import agents.test_planning as plan_agent
import agents.test_cases as tc_agent
import agents.test_code as code_agent
import agents.execution as exec_agent
import agents.reporting as report_agent
from github_pr import create_pr
from models import PipelineState

console = Console()
ORCHESTRATOR_MODEL = "claude-opus-4-6"

ORCHESTRATOR_SYSTEM = """You are the STLC Orchestrator — the central brain of the Software Testing Life Cycle pipeline.

You coordinate 15 specialized agents across 6 STLC stages. You never do the actual work yourself — you route, judge quality, and decide when to advance or retry.

Pipeline stages:
1. Requirement Analysis: fetch_linear_ticket → fetch_outline_doc → analyze_requirements
2. Test Planning: write_test_plan → create_linear_subtasks
3. Test Case Development: write_test_cases → review_test_cases (retry max 2x if NEEDS REWORK)
                          write_test_code → review_test_code (retry max 2x if NEEDS REWORK)
4. Environment Check: (environments are always running — skip to Stage 5)
5. Test Execution: run_tests → monitor_execution
6. Test Cycle Closure: generate_allure_report → write_closure_report → update_linear_ticket → notify_team

Rules:
- Run stages in order. Never skip Stage 1.
- If analyze_requirements returns AMBIGUITIES, stop and report them to the user — do not proceed.
- If a review returns NEEDS REWORK, re-run the writing step with the feedback. Max 2 retries.
- Stage 6 always runs regardless of test outcome.
- Be decisive. Don't over-iterate.
"""


def build_tools() -> list[dict]:
    return [
        {
            "name": "fetch_linear_ticket",
            "description": "Fetch the Linear ticket for requirement analysis.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "fetch_outline_doc",
            "description": "Fetch the Outline specification document.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "analyze_requirements",
            "description": "Analyze the Linear ticket and Outline doc to extract testable requirements.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "write_test_plan",
            "description": "Write a test plan from analyzed requirements.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "create_linear_subtasks",
            "description": "Create Linear subtasks from the test plan.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "write_test_cases",
            "description": "Write test cases from requirements.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "Feedback from previous review, if reworking"}
                },
                "required": []
            }
        },
        {
            "name": "review_test_cases",
            "description": "Review test cases. Returns APPROVED or NEEDS REWORK.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "write_test_code",
            "description": "Write automation code from test cases.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "feedback": {"type": "string", "description": "Feedback from previous review, if reworking"}
                },
                "required": []
            }
        },
        {
            "name": "review_test_code",
            "description": "Review automation code. Returns APPROVED or NEEDS REWORK.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "run_tests",
            "description": "Run REST Assured, Playwright, and Appium tests in parallel.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "monitor_execution",
            "description": "Summarize test execution results.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "generate_allure_report",
            "description": "Generate the Allure HTML report.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "write_closure_report",
            "description": "Write the test cycle closure report with verdict.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "update_linear_ticket",
            "description": "Update the Linear ticket status to reflect test outcome.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "New status: Done, In Review, etc."}
                },
                "required": ["status"]
            }
        },
        {
            "name": "notify_team",
            "description": "Send Slack and email notification with closure summary.",
            "input_schema": {"type": "object", "properties": {}, "required": []}
        },
    ]


def execute_tool(client: anthropic.Anthropic, tool_name: str, tool_input: dict, state: PipelineState) -> str:
    console.print(f"[bold yellow]→ {tool_name}[/bold yellow]")

    if tool_name == "fetch_linear_ticket":
        ticket = linear.fetch_ticket(state.linear_ticket_id)
        state.raw_requirements = json.dumps(ticket)
        return f"Ticket fetched: {ticket['title']}\nDescription: {ticket['description']}"

    elif tool_name == "fetch_outline_doc":
        doc = outline.fetch_doc(state.outline_doc_url)
        return f"Doc fetched: {doc['title']}\nContent length: {len(doc['text'])} chars"

    elif tool_name == "analyze_requirements":
        ticket = json.loads(state.raw_requirements)
        doc = outline.fetch_doc(state.outline_doc_url)
        state.analyzed_requirements = req_agent.analyze_requirements(client, ticket, doc)
        return state.analyzed_requirements

    elif tool_name == "write_test_plan":
        state.test_plan = plan_agent.write_test_plan(client, state.analyzed_requirements)
        return state.test_plan

    elif tool_name == "create_linear_subtasks":
        ticket = json.loads(state.raw_requirements)
        lines = [l.strip() for l in state.test_plan.split("\n") if l.strip().startswith(tuple("123456789"))]
        created = []
        for line in lines[:10]:
            title = line.lstrip("0123456789. ")
            issue_id = linear.create_subtask(
                parent_id=ticket["id"],
                title=title,
                description=f"Auto-generated STLC subtask for: {state.feature_name}"
            )
            created.append(issue_id)
            state.linear_subtask_ids.append(issue_id)
        return f"Created {len(created)} Linear subtasks: {', '.join(created)}"

    elif tool_name == "write_test_cases":
        feedback = tool_input.get("feedback", "")
        state.test_cases = tc_agent.write_test_cases(client, state.analyzed_requirements, feedback)
        return state.test_cases

    elif tool_name == "review_test_cases":
        state.test_cases_review = tc_agent.review_test_cases(
            client, state.test_cases, state.analyzed_requirements
        )
        return state.test_cases_review

    elif tool_name == "write_test_code":
        feedback = tool_input.get("feedback", "")
        state.test_code = code_agent.write_test_code(
            client, state.test_cases, state.tech_stack, feedback
        )
        return state.test_code

    elif tool_name == "review_test_code":
        state.test_code_review = code_agent.review_test_code(client, state.test_code)
        return state.test_code_review

    elif tool_name == "run_tests":
        run_results = runner.run_all_tests()
        state.execution_results = {k: vars(v) for k, v in run_results.items()}
        summary = "\n".join([
            f"{k}: {'PASS' if v.passed else 'FAIL'}" for k, v in run_results.items()
        ])
        return f"Tests complete:\n{summary}"

    elif tool_name == "monitor_execution":
        from tools.runner import RunResult
        run_results = {k: RunResult(**v) for k, v in state.execution_results.items()}
        summary = exec_agent.monitor_execution(client, run_results)
        return summary

    elif tool_name == "generate_allure_report":
        import os
        maven_path = os.environ.get("MAVEN_PROJECT_PATH", ".")
        try:
            state.allure_report_path = allure.generate_report(maven_path)
            return f"Allure report generated at: {state.allure_report_path}"
        except RuntimeError as e:
            return f"Allure report failed (non-critical): {e}"

    elif tool_name == "write_closure_report":
        state.closure_report = report_agent.write_closure_report(
            client,
            feature_name=state.feature_name,
            execution_summary=state.execution_results.get("summary", str(state.execution_results)),
            test_plan=state.test_plan,
        )
        state.pr_url = create_pr(
            feature_name=state.feature_name,
            test_cases=state.test_cases,
            test_code=state.test_code,
            closure_report=state.closure_report,
        )
        return f"Closure report written. PR created: {state.pr_url}"

    elif tool_name == "update_linear_ticket":
        ticket = json.loads(state.raw_requirements)
        status = tool_input.get("status", "Done")
        linear.update_ticket_status(ticket["id"], status)
        return f"Linear ticket {state.linear_ticket_id} updated to: {status}"

    elif tool_name == "notify_team":
        msg = (
            f"STLC Complete — {state.feature_name}\n"
            f"PR: {state.pr_url}\n"
            f"Allure: {state.allure_report_path}\n\n"
            f"{state.closure_report[:500]}"
        )
        notifier.send_slack(msg)
        notifier.send_email(
            subject=f"[STLC] {state.feature_name} — Cycle Complete",
            body=msg
        )
        return "Team notified via Slack and email."

    return f"Unknown tool: {tool_name}"


def run_pipeline(
    linear_ticket_id: str,
    outline_doc_url: str,
    feature_name: str,
    tech_stack: str = "REST Assured + Playwright + Appium",
    output_dir: str = "./stlc_output",
    repo_path: str | None = None,
) -> PipelineState:
    client = anthropic.Anthropic()
    state = PipelineState(
        linear_ticket_id=linear_ticket_id,
        outline_doc_url=outline_doc_url,
        feature_name=feature_name,
        tech_stack=tech_stack,
        output_dir=output_dir,
        repo_path=repo_path,
    )

    console.print(Panel(
        f"[bold]Feature:[/bold] {feature_name}\n"
        f"[bold]Ticket:[/bold] {linear_ticket_id}\n"
        f"[bold]Doc:[/bold] {outline_doc_url}",
        title="[bold magenta]STLC Orchestrator[/bold magenta]",
        border_style="magenta"
    ))

    tools = build_tools()
    messages = [{
        "role": "user",
        "content": (
            f"Run the full STLC pipeline for:\n\n"
            f"Feature: {feature_name}\n"
            f"Linear Ticket: {linear_ticket_id}\n"
            f"Outline Doc: {outline_doc_url}\n"
            f"Tech Stack: {tech_stack}\n\n"
            "Follow all 6 stages in order. Begin now."
        )
    }]

    iteration = 0
    max_iterations = 30

    while iteration < max_iterations:
        iteration += 1
        console.print(f"\n[dim]Orchestrator turn {iteration}...[/dim]")

        response = client.messages.create(
            model=ORCHESTRATOR_MODEL,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=ORCHESTRATOR_SYSTEM,
            tools=tools,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                console.print(f"\n[bold magenta]Orchestrator:[/bold magenta] {block.text}")

        if response.stop_reason == "end_turn":
            console.print("\n[bold green]STLC Pipeline complete![/bold green]")
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    try:
                        result = execute_tool(client, block.name, block.input, state)
                    except Exception as e:
                        result = f"Error in {block.name}: {str(e)}"
                        console.print(f"[red]Error:[/red] {result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result[:8000]
                    })

            messages.append({"role": "user", "content": tool_results})

    return state
