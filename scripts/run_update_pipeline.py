import subprocess
import sys

def run(cmd):
    print(f"→ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)

if __name__ == "__main__":
    run("python update_data.py")
    run("python normalize_netflix_txt.py")

