# main.py
import sys
import os
import anthropic
from dotenv import load_dotenv
from models import PipelineState
from orchestrator import run_pipeline

load_dotenv()

AGENTS = {
    "1": ("Full pipeline", "all"),
    "2": ("Requirements analysis", "requirements"),
    "3": ("Test planning", "test_planning"),
    "4": ("Test case writer", "test_cases"),
    "5": ("Test case reviewer", "test_cases_review"),
    "6": ("Appium locator extractor", "locators"),
    "7": ("Test code writer", "test_code"),
    "8": ("Test code reviewer", "test_code_review"),
    "9": ("Execution monitor", "execution"),
    "10": ("Closure report", "closure"),
}


def prompt(label, default=None):
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def pick_agent():
    print("\n🚀 Relay — STLC Multi-Agent Pipeline")
    print("─" * 40)
    print("Which agent do you want to run?\n")
    for key, (name, _) in AGENTS.items():
        print(f"  {key:>2}. {name}")
    print()
    choice = input("Enter number: ").strip()
    if choice not in AGENTS:
        print("❌ Invalid choice.")
        sys.exit(1)
    return AGENTS[choice]


def get_base_inputs():
    print()
    ticket = prompt("Linear ticket ID (e.g. QA-123)")
    outline_url = prompt("Outline doc URL")
    feature = prompt("Feature name (e.g. OCR Cheque)")
    if not ticket or not outline_url or not feature:
        print("❌ Ticket, Outline URL, and Feature are required.")
        sys.exit(1)
    return ticket, outline_url, feature


def run_single_agent(agent_key: str, state: PipelineState):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if agent_key == "requirements":
        from tools.linear import fetch_ticket
        from tools.outline import fetch_doc
        from agents.requirements import analyze_requirements
        print("\n▶ Fetching ticket and doc...")
        state.raw_requirements = fetch_ticket(state.linear_ticket_id) + "\n\n" + fetch_doc(state.outline_doc_url)
        print("▶ Analyzing requirements...")
        state.analyzed_requirements = analyze_requirements(client, state.raw_requirements, "")
        print(f"\n✅ Requirements:\n{state.analyzed_requirements}")

    elif agent_key == "test_planning":
        if not state.analyzed_requirements:
            state.analyzed_requirements = prompt("Paste analyzed requirements")
        from agents.test_planning import write_test_plan
        print("\n▶ Writing test plan...")
        state.test_plan = write_test_plan(client, state.analyzed_requirements)
        print(f"\n✅ Test Plan:\n{state.test_plan}")

    elif agent_key == "test_cases":
        if not state.analyzed_requirements:
            state.analyzed_requirements = prompt("Paste analyzed requirements")
        from agents.test_cases import write_test_cases
        print("\n▶ Writing test cases...")
        state.test_cases = write_test_cases(client, state.analyzed_requirements)
        print(f"\n✅ Test Cases:\n{state.test_cases}")

    elif agent_key == "test_cases_review":
        if not state.test_cases:
            state.test_cases = prompt("Paste test cases")
        if not state.analyzed_requirements:
            state.analyzed_requirements = prompt("Paste analyzed requirements")
        from agents.test_cases import review_test_cases
        print("\n▶ Reviewing test cases...")
        state.test_cases_review = review_test_cases(client, state.test_cases, state.analyzed_requirements)
        print(f"\n✅ Review:\n{state.test_cases_review}")

    elif agent_key == "locators":
        from tools.appium_locators import extract_locators
        from agents.locator_extractor import extract_relevant_locators
        output_path = prompt("UI dump output path", "/tmp/ui_dump.xml")
        print("\n▶ Extracting locators from device...")
        raw = extract_locators(output_path)
        if not state.analyzed_requirements:
            state.analyzed_requirements = prompt("Paste analyzed requirements")
        print("▶ Filtering relevant locators...")
        state.locator_map = extract_relevant_locators(client, raw, state.analyzed_requirements)
        print(f"\n✅ Locator Map:\n{state.locator_map}")

    elif agent_key == "test_code":
        if not state.test_cases:
            state.test_cases = prompt("Paste test cases")
        tech_stack = prompt("Tech stack", "REST Assured + Playwright + Appium")
        state.tech_stack = tech_stack
        from agents.test_code import write_test_code
        print("\n▶ Writing test code...")
        state.test_code = write_test_code(client, state.test_cases, state.tech_stack, locator_map=state.locator_map)
        print(f"\n✅ Test Code:\n{state.test_code[:500]}...")

    elif agent_key == "test_code_review":
        if not state.test_code:
            state.test_code = prompt("Paste test code")
        from agents.test_code import review_test_code
        print("\n▶ Reviewing test code...")
        state.test_code_review = review_test_code(client, state.test_code)
        print(f"\n✅ Review:\n{state.test_code_review}")

    elif agent_key == "execution":
        from tools.runner import run_all_tests
        from agents.execution import monitor_execution
        print("\n▶ Running tests...")
        results = run_all_tests(
            maven_project_path=os.getenv("MAVEN_PROJECT_PATH", ""),
            playwright_project_path=os.getenv("PLAYWRIGHT_PROJECT_PATH", ""),
            appium_project_path=os.getenv("APPIUM_PROJECT_PATH", ""),
        )
        state.execution_results = {k: vars(v) for k, v in results.items()}
        print("▶ Monitoring results...")
        summary = monitor_execution(client, results)
        print(f"\n✅ Execution Summary:\n{summary}")

    elif agent_key == "closure":
        if not state.test_plan:
            state.test_plan = prompt("Paste test plan")
        from agents.reporting import write_closure_report
        print("\n▶ Writing closure report...")
        state.closure_report = write_closure_report(
            client, state.feature_name, str(state.execution_results), state.test_plan
        )
        print(f"\n✅ Closure Report:\n{state.closure_report}")

    return state


def main():
    agent_name, agent_key = pick_agent()

    if agent_key == "all":
        ticket, outline_url, feature = get_base_inputs()
        tech_stack = prompt("Tech stack", "REST Assured + Playwright + Appium")
        output_dir = prompt("Output dir", "./stlc_output")
        print(f"\n▶ Running full pipeline for [{ticket}] — {feature}\n")
        state = run_pipeline(
            linear_ticket_id=ticket,
            outline_doc_url=outline_url,
            feature_name=feature,
            tech_stack=tech_stack,
            output_dir=output_dir,
        )
        print(f"\n✅ Done. PR: {state.pr_url}")
        print(f"📊 Allure: {state.allure_report_path}")
        print(f"📋 Closure: {state.closure_report[:200]}...")
    else:
        ticket, outline_url, feature = get_base_inputs()
        state = PipelineState(
            linear_ticket_id=ticket,
            outline_doc_url=outline_url,
            feature_name=feature,
        )
        print(f"\n▶ Running: {agent_name}\n")
        run_single_agent(agent_key, state)


if __name__ == "__main__":
    main()
