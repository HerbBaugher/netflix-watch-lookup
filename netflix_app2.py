import streamlit as st
import pandas as pd
from github import Github
import re

# ---------------------------
# GitHub secrets
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "data/Netflix_txt.txt"   # <--- FIXED PATH

# ---------------------------
# Load Netflix TXT from GitHub
# ---------------------------
def load_from_github():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        text = file.decoded_content.decode("utf-8")

        lines = text.splitlines()
        data = []

        date_pattern = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")

        current_title = ""

        for line in lines[1:]:  # skip header
            line = line.strip()
            if not line:
                continue

            date_match = date_pattern.search(line)

            if date_match:
                date_str = date_match.group()
                title_part = line[:date_match.start()].strip()

                full_title = (current_title + " " + title_part).strip()
                current_title = ""

                if full_title:
                    data.append([full_title, date_str])

            else:
                current_title = (current_title + " " + line).strip()

        df = pd.DataFrame(data, columns=["Title", "Date"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        return df

    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return None

# ---------------------------
# Save back to GitHub
# ---------------------------
def save_to_github(df):
    try:
        csv_data = df.to_csv(index=False, sep="\t")
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        repo.update_file(FILE_PATH, "Update Netflix history", csv_data, contents.sha)
        st.success("Updated on GitHub!")
    except Exception as e:
        st.error(f"Failed to save: {e}")

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📺 Netflix Watch Lookup & Editor")

df = load_from_github()

if df is not None:
    st.subheader("Edit Netflix Viewing History")
    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Save Changes"):
        save_to_github(edited_df)

    st.subheader("Search Your Watch History")
    query = st.text_input("Enter a title")

    if query:
        matches = df[df["Title"].str.lower().str.contains(query.lower(), na=False)]

        if matches.empty:
            st.warning(f"No results for '{query}'.")
        else:
            grouped = matches.groupby("Title")

            for title, group in grouped:
                st.markdown(f"### {title}")
                st.write(f"Times Watched: {len(group)}")
                st.write(f"Most Recent: {group['Date'].max().date()}")
                st.write("All Dates:")
                for d in group["Date"].sort_values():
                    st.write(f"- {d.date()}")
                st.markdown("---")

