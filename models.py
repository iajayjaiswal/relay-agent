from dataclasses import dataclass, field


@dataclass
class PipelineState:
    # Input
    linear_ticket_id: str
    outline_doc_url: str
    feature_name: str

    # Stage 1 outputs
    raw_requirements: str = ""
    analyzed_requirements: str = ""

    # Stage 2 outputs
    test_plan: str = ""
    linear_subtask_ids: list = field(default_factory=list)

    # Stage 3 inputs (locator extraction)
    locator_map: str = ""

    # Stage 3 outputs
    test_cases: str = ""
    test_cases_review: str = ""
    test_code: str = ""
    test_code_review: str = ""
    pr_url: str = ""

    # Stage 5 outputs
    execution_results: dict = field(default_factory=dict)

    # Stage 6 outputs
    allure_report_path: str = ""
    closure_report: str = ""

    # Control
    tech_stack: str = "REST Assured + Playwright + Appium"
    output_dir: str = "./stlc_output"
    repo_path: str | None = None
