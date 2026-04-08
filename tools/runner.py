import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass
class RunResult:
    suite: str
    passed: bool
    output: str
    returncode: int


def _run_maven(project_path: str, extra_args: list = None) -> RunResult:
    """Run Maven test suite."""
    cmd = ["mvn", "test"] + (extra_args or [])
    result = subprocess.run(
        cmd,
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=600
    )
    output = result.stdout + result.stderr
    return RunResult(
        suite="rest_assured",
        passed=result.returncode == 0,
        output=output,
        returncode=result.returncode
    )


def _run_playwright(project_path: str) -> RunResult:
    """Run Playwright test suite."""
    result = subprocess.run(
        ["npx", "playwright", "test"],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=600
    )
    output = result.stdout + result.stderr
    return RunResult(
        suite="playwright",
        passed=result.returncode == 0,
        output=output,
        returncode=result.returncode
    )


def _run_appium(project_path: str) -> RunResult:
    """Run Appium mobile test suite via Maven."""
    result = subprocess.run(
        ["mvn", "test", "-Dsuite=mobile"],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=900
    )
    output = result.stdout + result.stderr
    return RunResult(
        suite="appium",
        passed=result.returncode == 0,
        output=output,
        returncode=result.returncode
    )


def run_all_tests() -> dict[str, RunResult]:
    """
    Run REST Assured, Playwright, and Appium test suites in parallel.
    Returns a dict of suite name → RunResult.
    """
    maven_path = os.environ.get("MAVEN_PROJECT_PATH", ".")
    playwright_path = os.environ.get("PLAYWRIGHT_PROJECT_PATH", ".")
    appium_path = os.environ.get("APPIUM_PROJECT_PATH", ".")

    tasks = {
        "rest_assured": lambda: _run_maven(maven_path),
        "playwright": lambda: _run_playwright(playwright_path),
        "appium": lambda: _run_appium(appium_path),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fn): name for name, fn in tasks.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = RunResult(
                    suite=name,
                    passed=False,
                    output=f"Runner error: {str(e)}",
                    returncode=-1
                )
    return results
