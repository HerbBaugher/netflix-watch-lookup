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
def load_from_github():
    """Load Netflix_txt.txt directly from GitHub."""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file_content = repo.get_contents(FILE_PATH)
        content = file_content.decoded_content.decode("utf-8")
        df = pd.read_csv(io.StringIO(content), sep=r"\s{2,}", engine="python")
        df.columns = df.columns.str.strip()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        return df
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return None

def save_to_github(df):
    """Save edited dataframe back to GitHub."""
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

# Streamlit version check
version = tuple(map(int, st.__version__.split(".")))
if version < (1, 32):
    st.warning("⚠️ Editable table requires Streamlit 1.32+. Please upgrade Streamlit.")
    st.stop()

# Load data from GitHub
df = load_from_github()

if df is not None:
    st.info("You can edit the table below. After editing, click 'Save Changes' to update GitHub.")
    
    # Editable table
    edited_df = st.data_editor(df, num_rows="dynamic")

    # Save button
    if st.button("Save Changes"):
        save_to_github(edited_df)

# Search box
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
