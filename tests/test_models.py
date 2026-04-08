from models import PipelineState


def test_pipeline_state_defaults():
    state = PipelineState(
        linear_ticket_id="QA-123",
        outline_doc_url="https://outline.test/doc/abc",
        feature_name="OCR Cheque"
    )
    assert state.linear_ticket_id == "QA-123"
    assert state.outline_doc_url == "https://outline.test/doc/abc"
    assert state.feature_name == "OCR Cheque"
    assert state.raw_requirements == ""
    assert state.analyzed_requirements == ""
    assert state.test_plan == ""
    assert state.linear_subtask_ids == []
    assert state.test_cases == ""
    assert state.test_cases_review == ""
    assert state.test_code == ""
    assert state.test_code_review == ""
    assert state.pr_url == ""
    assert state.execution_results == {}
    assert state.allure_report_path == ""
    assert state.closure_report == ""
    assert state.tech_stack == "REST Assured + Playwright + Appium"
    assert state.output_dir == "./stlc_output"
    assert state.repo_path is None
