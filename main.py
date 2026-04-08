# main.py
import argparse
from dotenv import load_dotenv
from orchestrator import run_pipeline

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="STLC Orchestrator Agent")
    parser.add_argument("--ticket", required=True, help="Linear ticket ID (e.g. QA-123)")
    parser.add_argument("--outline-url", required=True, help="Outline document URL")
    parser.add_argument("--feature", required=True, help="Feature name (e.g. 'OCR Cheque')")
    parser.add_argument(
        "--tech-stack",
        default="REST Assured + Playwright + Appium",
        help="Test tech stack"
    )
    parser.add_argument("--output-dir", default="./stlc_output", help="Output directory")
    args = parser.parse_args()

    state = run_pipeline(
        linear_ticket_id=args.ticket,
        outline_doc_url=args.outline_url,
        feature_name=args.feature,
        tech_stack=args.tech_stack,
        output_dir=args.output_dir,
    )

    print(f"\n✅ Done. PR: {state.pr_url}")
    print(f"📊 Allure: {state.allure_report_path}")
    print(f"📋 Closure: {state.closure_report[:200]}...")


if __name__ == "__main__":
    main()
