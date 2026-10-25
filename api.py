
from fastapi import FastAPI
from pathlib import Path
import subprocess
import sys
import json
from datetime import datetime

app = FastAPI(title="OmniSight API")


@app.get("/")
def home():
    return {
        "message": "Welcome to OmniSight!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def run_script(script_path, project_folder):
    return subprocess.run(
        [sys.executable, str(script_path)],
        cwd=project_folder,
        capture_output=True,
        text=True,
        timeout=60
    )


@app.post("/run-test")
def run_test():
    project_folder = Path(__file__).resolve().parent
    test_file = project_folder / "browser_test.py"
    heal_file = project_folder / "self_heal.py"
    results_folder = project_folder / "test_results"

    results_folder.mkdir(exist_ok=True)

    # Run the original browser test
    try:
        test = run_script(test_file, project_folder)

        original_passed = (
            test.returncode == 0
            and "STATUS: PASS" in test.stdout
            and "STATUS: FAIL" not in test.stdout
        )

        repair_attempted = False
        repair_success = None
        repair_output = ""

        # Attempt self-healing only if the test fails
        if not original_passed:
            repair_attempted = True
            repair = run_script(heal_file, project_folder)
            repair_output = repair.stdout

            repair_success = (
                repair.returncode == 0
                and "SELF-HEALING SUCCESS" in repair.stdout
                and "FIX INCOMPLETE" not in repair.stdout
            )

        final_result = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "success": original_passed or repair_success is True,
            "original_test_passed": original_passed,
            "original_test_output": test.stdout,
            "original_test_errors": test.stderr,
            "repair_attempted": repair_attempted,
            "repair_success": repair_success,
            "repair_output": repair_output
        }

    except subprocess.TimeoutExpired:
        final_result = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "success": False,
            "original_test_passed": False,
            "original_test_output": "",
            "original_test_errors": "Browser test timed out.",
            "repair_attempted": False,
            "repair_success": None,
            "repair_output": ""
        }

    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    result_file = results_folder / f"test_result_{timestamp}.json"

    with result_file.open("w", encoding="utf-8") as file:
        json.dump(final_result, file, indent=4)

    return {
        **final_result,
        "result_file": str(result_file.relative_to(project_folder))
    }
