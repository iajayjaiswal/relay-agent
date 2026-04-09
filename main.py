# main.py
import sys
from dotenv import load_dotenv
from orchestrator import run_pipeline

load_dotenv()


def prompt(label, default=None):
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or default


def main():
    print("🚀 Relay — STLC Multi-Agent Pipeline")
    print("─" * 40)
    ticket = prompt("Linear ticket ID (e.g. QA-123)")
    outline_url = prompt("Outline doc URL")
    feature = prompt("Feature name (e.g. OCR Cheque)")
    tech_stack = prompt("Tech stack", "REST Assured + Playwright + Appium")
    output_dir = prompt("Output dir", "./stlc_output")

    if not ticket or not outline_url or not feature:
        print("❌ Ticket, Outline URL, and Feature are required.")
        sys.exit(1)

    print(f"\n▶ Starting pipeline for [{ticket}] — {feature}\n")

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


if __name__ == "__main__":
    main()
