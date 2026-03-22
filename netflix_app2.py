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
# Load Netflix file from GitHub
# ---------------------------
def load_github_csv():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file_content = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(file_content.decoded_content.decode("utf-8")), sep="\s+", engine="python")
        # Ensure proper columns
        df.columns = ["Title", "Date"]
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# ---------------------------
# Save dataframe back to GitHub
# ---------------------------
def save_to_github(df, commit_message="Update Netflix watch history"):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, sep=",")
        content = csv_buffer.getvalue()
        file = repo.get_contents(FILE_PATH)
        repo.update_file(FILE_PATH, commit_message, content, file.sha)
        st.success("✅ Netflix history updated on GitHub!")
    except Exception as e:
        st.error(f"Error saving file: {e}")

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📺 Netflix Watch History Editor")

df = load_github_csv()

if df is not None:
    st.info("You can edit the table below. After editing, click 'Save Changes' to update GitHub.")
    
    # Editable table
    edited_df = st.experimental_data_editor(df, num_rows="dynamic")

    # Save button
    if st.button("Save Changes"):
        save_to_github(edited_df)

else:
    st.warning("No data loaded yet. Make sure your GitHub secrets and CSV file are set correctly.")
