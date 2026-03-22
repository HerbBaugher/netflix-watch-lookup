import streamlit as st
import pandas as pd
from github import Github
from datetime import datetime
import re
import io

# ---------------------------
# GitHub secrets
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "data/Netflix_txt.txt"   # CSV stored in a .txt file

# ---------------------------
# Load CSV from GitHub
# ---------------------------
def load_from_github():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        text = file.decoded_content.decode("utf-8")

        # Parse CSV (Title,Date)
        df = pd.read_csv(io.StringIO(text))

        # Convert Date column
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        return df

    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")
        return None

# ---------------------------
# Save CSV back to GitHub
# ---------------------------
def save_to_github(df):
    try:
        csv_data = df.to_csv(index=False)

        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)

        repo.update_file(
            FILE_PATH,
            "Update Netflix history",
            csv_data,
            contents.sha
        )

        st.success("Updated on GitHub!")

    except Exception as e:
        st.error(f"Failed to save: {e}")

# ---------------------------
# Episode extraction
# ---------------------------
def extract_episode(title):
    match = re.search(r"Season\s+(\d+)", title, re.IGNORECASE)
    return int(match.group(1)) if match else None

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📺 Netflix Watch History — Lookup, Stats & Editor")

# Refresh Now button
if st.button("🔄 Refresh Now"):
    st.cache_data.clear()
    st.rerun()

df = load_from_github()

if df is None or df.empty:
    st.error("No data found. Check file format or GitHub path.")
    st.stop()

# ---------------------------
# Dashboard
# ---------------------------
st.subheader("📊 Recently Watched")
recent = df.sort_values("Date", ascending=False).head(10)
st.dataframe(recent)

# Monthly stats
st.subheader("📅 Monthly Watch Count")
df["Month"] = df["Date"].dt.to_period("M")
monthly = df.groupby("Month").size().reset_index(name="Count")
st.bar_chart(monthly.set_index("Month"))

# Episode grouping
st.subheader("🎬 Episodes by Season")
df["Season"] = df["Title"].apply(extract_episode)
episodes = df.dropna(subset=["Season"])
if not episodes.empty:
    st.dataframe(episodes.sort_values(["Season", "Date"], ascending=[True, False]))
else:
    st.info("No episodic content detected.")

# ---------------------------
# Search
# ---------------------------
st.subheader("🔍 Search Your Watch History")
query = st.text_input("Enter a title or keyword")

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

# ---------------------------
# Editor
# ---------------------------
st.subheader("✏️ Edit Netflix Viewing History")
edited_df = st.data_editor(df.drop(columns=["Month", "Season"]), num_rows="dynamic")

if st.button("Save Changes"):
    save_to_github(edited_df)

