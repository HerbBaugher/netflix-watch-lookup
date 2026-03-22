import streamlit as st
import pandas as pd
from github import Github
from io import StringIO

# ---------------------------
# GITHUB SETTINGS
# ---------------------------
# Make sure your secrets.toml has:
# GITHUB_TOKEN = "your_token_here"
# REPO_NAME = "HerbBaugher/netflix-watch-lookup"
# FILE_PATH = "data/Netflix_txt.txt"

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data
def load_data():
    contents = repo.get_contents(FILE_PATH)
    text = contents.decoded_content.decode("utf-8")
    # Space-separated data, some titles span multiple lines
    lines = []
    for line in text.splitlines():
        if line.strip():  # skip empty lines
            lines.append(line)
    # Fix for multi-line titles
    rows = []
    temp_title = ""
    for line in lines[1:]:  # skip header
        parts = line.rsplit(maxsplit=1)
        if len(parts) == 2:
            title, date = parts
            if temp_title:
                title = temp_title + " " + title
                temp_title = ""
            rows.append([title.strip(), date.strip()])
        else:
            # title split across lines
            temp_title += line.strip() + " "
    df = pd.DataFrame(rows, columns=["Title", "Date"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df, contents

df, file_contents = load_data()

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("📺 Netflix Watch Lookup")

# Search bar
query = st.text_input("Search for a title")

if query:
    matches = df[df["Title"].str.contains(query, case=False, na=False)]
    if matches.empty:
        st.warning(f"No watch history found for **{query}**.")
    else:
        st.subheader("Matching Titles")
        for title, group in matches.groupby("Title"):
            latest = group["Date"].max()
            st.markdown(f"### {title}")
            st.write(f"**Times Watched:** {len(group)}")
            st.write(f"**Most Recent Watch:** {latest.date()}")
            st.write("**All Dates Watched:**")
            for date in group["Date"].sort_values():
                st.write(f"- {date.date()}")
            st.markdown("---")

st.info("You can edit the table below. After editing, click 'Save Changes' to update GitHub.")

# Editable table
edited_df = st.experimental_data_editor(df, num_rows="dynamic")

# ---------------------------
# SAVE TO GITHUB
# ---------------------------
def save_to_github(updated_df):
    csv_buffer = StringIO()
    updated_df.to_csv(csv_buffer, index=False, sep=" ")
    repo.update_file(
        path=FILE_PATH,
        message="Update Netflix watch history via Streamlit",
        content=csv_buffer.getvalue(),
        sha=file_contents.sha
    )
    st.success("Netflix_txt.txt updated on GitHub!")

if st.button("Save Changes"):
    save_to_github(edited_df)
