import streamlit as st
import pandas as pd
from github import Github
import io
import re
from datetime import datetime

# ---------------------------
# GitHub secrets
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

# ---------------------------
# Custom parser for Netflix_txt.txt
# ---------------------------
def parse_netflix_file(text):
    lines = text.splitlines()
    data = []
    current_title = ""

    date_pattern = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}$")

    for line in lines[1:]:  # skip header
        line = line.strip()
        if not line:
            continue
        # Check if line ends with a date
        match = date_pattern.search(line)
        if match:
            date_str = match.group()
            title = line[:match.start()].strip()
            if current_title:
                title = current_title + " " + title
                current_title = ""
            data.append({"Title": title, "Date": date_str})
        else:
            # Continuation of previous title
            current_title = (current_title + " " + line).strip()
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df

# ---------------------------
# Load Netflix file from GitHub
# ---------------------------
def load_github_txt():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file_content = repo.get_contents(FILE_PATH)
        text = file_content.decoded_content.decode("utf-8")
        df = parse_netflix_file(text)
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
        # Convert back to space-separated text
        lines = ["Title                  Date"]
        for _, row in df.iterrows():
            lines.append(f"{row['Title']}            {row['Date'].strftime('%-m/%-d/%y')}")
        content = "\n".join(lines)
        file = repo.get_contents(FILE_PATH)
        repo.update_file(FILE_PATH, commit_message, content, file.sha)
        st.success("✅ Netflix history updated on GitHub!")
    except Exception as e:
        st.error(f"Error saving file: {e}")

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📺 Netflix Watch History Editor")

df = load_github_txt()

if df is not None:
    st.info("You can edit the table below. After editing, click 'Save Changes' to update GitHub.")
    
    edited_df = st.experimental_data_editor(df, num_rows="dynamic")

    if st.button("Save Changes"):
        save_to_github(edited_df)

else:
    st.warning("No data loaded yet. Make sure your GitHub secrets and CSV file are set correctly.")
