
from fastapi import FastAPI
from pathlib import Path
import subprocess
import sys

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

    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=project_folder,
        capture_output=True,
        text=True,
        timeout=60
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "errors": result.stderr
    }
