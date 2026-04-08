import os
import subprocess


def generate_report(project_path: str) -> str:
    """
    Generate an Allure HTML report from test results.
    Returns the path to the generated report directory.
    """
    result = subprocess.run(
        ["mvn", "allure:report"],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=120
    )
    report_path = os.path.join(project_path, "target", "site", "allure-maven-plugin")
    if result.returncode != 0:
        raise RuntimeError(f"Allure report generation failed:\n{result.stderr}")
    return report_path
