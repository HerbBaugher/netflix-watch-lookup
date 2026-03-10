import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import io
from datetime import datetime
from odf.opendocument import load
from odf.text import P

df = None


# ---------------------------
# READ ODT FILE (EXTRACT TEXT)
# ---------------------------
def read_odt(file):
    textdoc = load(file)
    lines = []
    for p in textdoc.getElementsByType(P):
        lines.append(str(p))
    csv_text = "\n".join(lines)
    return pd.read_csv(io.StringIO(csv_text))


# ---------------------------
# LOAD FILE
# ---------------------------
def load_file():
    global df
    file_path = filedialog.askopenfilename(
        title="Select Netflix History File",
        initialdir=r"C:\Python practice files",
        filetypes=[("Netflix Files", "*.csv *.odt"), ("All Files", "*.*")]
    )

    if not file_path:
        return

    try:
        if file_path.lower().endswith(".odt"):
            df = read_odt(file_path)
        else:
            df = pd.read_csv(file_path, encoding="latin1", engine="python", on_bad_lines="skip")

        # Clean column names
        df.columns = (
            df.columns.str.strip()
            .str.replace('"', '', regex=False)
            .str.replace("'", "", regex=False)
            .str.replace("ï»¿", "", regex=False)
        )

        if "Title" not in df.columns or "Date" not in df.columns:
            messagebox.showerror("Error", f"Columns detected: {df.columns.tolist()}\nFile must contain Title and Date")
            df = None
            return

        # Convert dates
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%y", errors="coerce")
        df.dropna(subset=["Date"], inplace=True)

        messagebox.showinfo("Success", "Netflix history loaded")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ---------------------------
# SEARCH TITLE (PARTIAL MATCH)
# ---------------------------
def search_title():
    if df is None:
        messagebox.showerror("Error", "Load a Netflix file first")
        return

    query = title_entry.get().strip().lower()
    results_text.delete(1.0, tk.END)

    if not query:
        messagebox.showerror("Error", "Enter a title to search")
        return

    # Partial match (case-insensitive)
    matches = df[df["Title"].str.lower().str.contains(query, na=False)]

    if matches.empty:
        results_text.insert(tk.END, f"No watch history found for '{query}'.\n")
        return

    results_text.insert(tk.END, f"Watch history for '{query}':\n\n")

    # Show all watch dates
    for date in matches["Date"].sort_values():
        results_text.insert(tk.END, f"- {date.date()}\n")

    # Show most recent watch date
    latest = matches["Date"].max()
    results_text.insert(tk.END, f"\nMost recent watch: {latest.date()}\n")


# ---------------------------
# GUI
# ---------------------------
root = tk.Tk()
root.title("Netflix Watch Lookup")
root.geometry("550x400")

# Load button
ttk.Button(root, text="Load Netflix History", command=load_file).pack(pady=10)

# Search area
frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Enter Title (partial or full):").pack(side=tk.LEFT, padx=5)
title_entry = ttk.Entry(frame, width=40)
title_entry.pack(side=tk.LEFT, padx=5)

ttk.Button(frame, text="Search", command=search_title).pack(side=tk.LEFT, padx=5)

# Results
results_frame = ttk.LabelFrame(root, text="Results")
results_frame.pack(fill="both", expand=True, padx=10, pady=10)

results_text = tk.Text(results_frame)
results_text.pack(fill="both", expand=True)

root.mainloop()