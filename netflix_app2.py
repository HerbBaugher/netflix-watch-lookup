import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime
import re

# ---------------------------
# GitHub secrets
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

# ---------------------------
# Helper functions
# ---------------------------
def load_from_github():
    """Load Netflix_txt.txt from GitHub and parse multi-line titles."""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = repo.get_contents(FILE_PATH)
        content = file_content.decoded_content.decode("utf-8")

        lines = content.splitlines()
        data = []
        current_title = ""
        date_pattern = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}")  # matches dates like 3/8/26

        for line in lines[1:]:  # skip header
            line = line.strip()
            if not line:
                continue
            date_match = date_pattern.search(line)
            if date_match:
                date_str = date_match.group()
                title = (current_title + " " + line[:date_match.start()]).strip()
                data.append([title, date_str])
                current_title = ""
            else:
                current_title += " " + line if current_title else line

        df = pd.DataFrame(data, columns=["Title", "Date"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        return df
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return None

def save_to_github(df):
    """Save edited dataframe back to GitHub."""
    try:
        csv_data = df.to_csv(index=False, sep="\t")
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        repo.update_file(contents.path, "Update Netflix watch history", csv_data, contents.sha)
        st.success("✅ File updated on GitHub!")
    except Exception as e:
        st.error(f"Failed to save to GitHub: {e}")

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📺 Netflix Watch Lookup")

version = tuple(map(int, st.__version__.split(".")))
if version < (1, 32):
    st.warning("⚠️ Editable table requires Streamlit 1.32+. Please upgrade Streamlit.")
    st.stop()

df = load_from_github()

if df is not None:
    st.info("You can edit the table below. After editing, click 'Save Changes' to update GitHub.")

    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Save Changes"):
        save_to_github(edited_df)

    query = st.text_input("Search for a title")
    if query:
        matches = df[df["Title"].str.lower().str.contains(query.lower(), na=False)]
        if matches.empty:
            st.warning(f"No watch history found for **{query}**.")
        else:
            st.subheader("Matching Titles")
            grouped = matches.groupby("Title")
            for title, group in grouped:
                latest = group["Date"].max()
                st.markdown(f"### {title}")
                st.write(f"**Times Watched:** {len(group)}")
                st.write(f"**Most Recent Watch:** {latest.date()}")
                st.write("**All Dates Watched:**")
                for date in group["Date"].sort_values():
                    st.write(f"- {date.date()}")
                st.markdown("---")
