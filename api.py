
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



@app.post("/run-test")
def run_test():
    project_folder = Path(__file__).resolve().parent
    test_file = project_folder / "browser_test.py"
    results_folder = project_folder / "test_results"

    results_folder.mkdir(exist_ok=True)

    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=project_folder,
        capture_output=True,
        text=True,
        timeout=60
    )

    test_result = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "success": result.returncode == 0,
        "output": result.stdout,
        "errors": result.stderr
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    result_file = results_folder / f"test_result_{timestamp}.json"

    with result_file.open("w", encoding="utf-8") as file:
        json.dump(test_result, file, indent=4)

    return {
        **test_result,
        "result_file": str(result_file.relative_to(project_folder))
    }
