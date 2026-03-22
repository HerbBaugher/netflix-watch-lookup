import streamlit as st
import pandas as pd
import io
from datetime import datetime
from github import Github

# ---------------------------
# GITHUB SECRETS
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------
def read_netflix_file(file_content):
    """
    Read Netflix space-separated text data into a DataFrame.
    Handles multi-line titles.
    """
    lines = file_content.splitlines()
    titles = []
    dates = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # If last 1 or 2 tokens match a date pattern
        parts = line.rsplit(" ", 2)
        try:
            # Try parsing the last token as date
            date_candidate = parts[-1]
            date_obj = pd.to_datetime(date_candidate, errors="coerce")
            if pd.notna(date_obj):
                title = " ".join(parts[:-1])
                if buffer:
                    title = buffer + " " + title
                    buffer = ""
                titles.append(title.strip())
                dates.append(date_obj)
            else:
                buffer = (buffer + " " + line).strip()
        except Exception:
            buffer = (buffer + " " + line).strip()

    df = pd.DataFrame({"Title": titles, "Date": dates})
    return df

def load_dataframe_from_github():
    file_content = repo.get_contents(FILE_PATH).decoded_content.decode("utf-8")
    df = read_netflix_file(file_content)
    return df

def save_dataframe_to_github(df, commit_message="Update Netflix history"):
    # Convert dataframe to CSV string
    csv_str = df.to_csv(index=False, header=False)
    file = repo.get_contents(FILE_PATH)
    repo.update_file(file.path, commit_message, csv_str, file.sha)

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("📺 Netflix Watch Lookup & Editor")

# Load data
df = load_dataframe_from_github()

st.write(f"ROWS LOADED: {len(df)}")

# Search feature
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

# Editable table
st.subheader("Edit Netflix History")

try:
    edited_df = st.experimental_data_editor(df, num_rows="dynamic")
    if st.button("Save Changes"):
        save_dataframe_to_github(edited_df)
        st.success("Changes saved to GitHub!")
except AttributeError:
    st.dataframe(df)
    st.warning("Editable table requires Streamlit 1.22+")
