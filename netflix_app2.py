import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# ---------------------------
# GitHub secrets
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

# ---------------------------
# Helper functions
# ---------------------------
def load_text_file(file):
    """Load space-separated Netflix_txt.txt file with 'Title' and 'Date' columns."""
    try:
        # Split by at least two spaces
        df = pd.read_csv(file, sep=r"\s{2,}", engine="python", header=0)
        df.columns = df.columns.str.strip()
        if "Title" not in df.columns or "Date" not in df.columns:
            st.error(f"Columns detected: {df.columns.tolist()}. Must include 'Title' and 'Date'.")
            return None
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def save_to_github(df):
    """Save the edited dataframe back to GitHub as CSV."""
    try:
        csv_data = df.to_csv(index=False)
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

# Check Streamlit version
version = tuple(map(int, st.__version__.split(".")))
if version < (1, 32):
    st.warning("⚠️ Editable table requires Streamlit 1.32+. Please upgrade Streamlit.")
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Upload Netflix history file (txt or csv)", type=["txt", "csv"]
)

df = None
if uploaded_file:
    df = load_text_file(uploaded_file)

# Show dataframe and editable table
if df is not None:
    st.info("You can edit the table below. After editing, click 'Save Changes' to update GitHub.")
    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Save Changes"):
        save_to_github(edited_df)

# Search functionality
if df is not None:
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
