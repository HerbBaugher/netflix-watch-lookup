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
    """Load Netflix_txt.txt from GitHub and correctly parse multi-line titles."""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = repo.get_contents(FILE_PATH)
        content = file_content.decoded_content.decode("utf-8")

        lines = content.splitlines()
        data = []

        # Netflix TXT format: Title may span multiple lines until a date appears
        date_pattern = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")

        current_title = ""

        for raw in lines[1:]:  # skip header
            line = raw.strip()
            if not line:
                continue

            date_match = date_pattern.search(line)

            if date_match:
                # Extract date
                date_str = date_match.group()

                # Extract title portion on the same line
                title_part = line[:date_match.start()].strip()

                # Combine with previous accumulated title lines
                full_title = (current_title + " " + title_part).strip()

                if full_title:
                    data.append([full_title, date_str])

                # Reset for next title
                current_title = ""

            else:
                # No date → this is part of a multi-line title
                current_title = (current_title + " " + line).strip()

        # Build DataFrame
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

