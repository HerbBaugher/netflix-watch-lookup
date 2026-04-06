import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent

def run_step(label, script_name):
    script_path = ROOT / script_name
    print(f"\n=== {label} ===")
    print(f"Looking for: {script_path}")

    if not script_path.exists():
        print(f"✗ ERROR: File not found: {script_path}")
        sys.exit(1)

    cmd = f"python {script_path}"
    print(f"→ Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"✗ FAILED: {label}")
        sys.exit(result.returncode)
    print(f"✓ SUCCESS: {label}")

if __name__ == "__main__":
    print(f"Working directory: {ROOT}")

    # Only run the merged auto_update.py now
    run_step("Auto update + normalize TXT", "auto_update.py")

    print("\nPipeline completed successfully.")
