import os
import sys
from datetime import datetime

# Path to your Netflix TXT file
FILE_PATH = "data/Netflix_txt.txt"


def load_text_file(path: str) -> list[str]:
    """Load the raw TXT file as a list of lines."""
    if not os.path.exists(path):
        print(f"File not found: {path}. Creating a new one.")
        return ["Title,Date\n"]  # keep header for consistency

    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def append_heartbeat(lines: list[str]) -> list[str]:
    """Append a TXT‑style heartbeat line with no comma."""
    heartbeat = f"Auto-update heartbeat{datetime.now().strftime('%m/%d/%y')}"
    lines.append(heartbeat)
    return lines


def save_text_file(lines: list[str], path: str):
    """Save the file back in TXT format."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")

    print(f"Updated data saved to {path}")


def main():
    # Allow override via environment or CLI
    data_path = os.environ.get("DATA_FILE", FILE_PATH)

    if len(sys.argv) > 1:
        data_path = sys.argv[1]

    lines = load_text_file(data_path)
    lines = append_heartbeat(lines)
    save_text_file(lines, data_path)


if __name__ == "__main__":
    main()

