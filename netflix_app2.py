import streamlit as st
import pandas as pd
from github import Github
import re
from datetime import datetime

# ---------------------------
# GitHub secrets
# ---------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "data/Netflix_txt.txt"

# ---------------------------
# Load Netflix TXT from GitHub
# ---------------------------
def load_from_github():
    """Load Netflix_txt.txt from GitHub and correctly parse multi-line titles."""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        text = file.decoded_content.decode("utf-8")

        lines = text.splitlines()
        data = []

        date_pattern = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")

        buffer = []  # holds multi-line title parts

        for line in lines[1:]:  # skip header
            line = line.rstrip()

            # Look for date at end of line
            match = date_pattern.search(line)

            if match:
                # Extract date
                date_str = match.group()

                # Extract title portion on this line
                title_part = line[:match.start()].strip()

                # Add final line of title to buffer
                if title_part:
                    buffer.append(title_part)

                # Combine all buffered lines into one title
                full_title = " ".join(buffer).strip()

                if full_title:
                    data.append([full_title, date_str])

                # Reset buffer for next title
                buffer = []

            else:
                # No date → this is part of a multi-line title
                if line.strip():
                    buffer.append(line.strip())

        # Build DataFrame
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
        txt_data = "Title\tDate\n"
        for _, row in df.iterrows():
            txt_data += f"{row['Title']}\t{row['Date'].strftime('%-m/%-d/%y')}\n"

        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        repo.update_file(FILE_PATH, "Update Netflix history", txt_data, contents.sha)
        st.success("Updated on GitHub!")
    except Exception as e:
        st.error(f"Failed to save: {e}")

# ---------------------------
# Episode extraction
# ---------------------------
def extract_episode(title):
    """
    Extracts season/episode info from titles like:
    - Season 3: Razzmatazz
    - Season 3: Lockstep
    - Season 3: Truth Be Told
    """
    season_match = re.search(r"Season\s+(\d+)", title, re.IGNORECASE)
    if season_match:
        season = int(season_match.group(1))
        return season
    return None

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("📺 Netflix Watch History — Lookup, Stats & Editor")

# Auto-refresh every 30 seconds
st_autorefresh = st.experimental_rerun

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

