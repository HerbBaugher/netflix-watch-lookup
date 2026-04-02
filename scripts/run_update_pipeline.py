import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

def run_step(label, cmd):
    print(f"\n=== {label} ===")
    print(f"→ Running: {cmd}")

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"✗ FAILED: {label}")
        sys.exit(result.returncode)

    print(f"✓ SUCCESS: {label}")


if __name__ == "__main__":
    # Ensure we are in repo root
    print(f"Working directory: {ROOT}")
    print(f"Scripts directory: {SCRIPTS}")

    # Step 1 — update data
    run_step(
        "Update data",
        f"python {SCRIPTS / 'update_data.py'}"
    )

    # Step 2 — normalize Netflix TXT
    run_step(
        "Normalize Netflix TXT",
        f"python {SCRIPTS / 'normalize_netflix_txt.py'}"
    )

    print("\nPipeline completed successfully.")
