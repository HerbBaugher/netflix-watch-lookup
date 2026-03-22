import streamlit as st
import pandas as pd
import io
import base64
from github import Github
from datetime import datetime

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Netflix Watch Lookup", layout="wide")
st.title("📺 Netflix Watch Lookup & Editor")

# ---------------------------
# LOAD DATA FROM GITHUB
# ---------------------------
@st.cache_data(show_spinner=True)
def load_data():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        file = repo.get_contents(st.secrets["FILE_PATH"])
        content = base64.b64decode(file.content).decode("utf-8")

        # Attempt CSV parsing
        df = pd.read_csv(io.StringIO(content), sep=",")  # change sep="\t" if your file uses tabs
        df.columns = df.columns.str.strip()  # clean whitespace

        # Validate columns
        if "Title" not in df.columns or "Date" not in df.columns:
            st.error(f"Columns detected: {df.columns.tolist()}. Must include 'Title' and 'Date'.")
            return None, None

        # Convert Date to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        return df, file.sha

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None, None

# ---------------------------
# SAVE DATA BACK TO GITHUB
# ---------------------------
def save_to_github(df, sha):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])

        csv_bytes = df.to_csv(index=False).encode("utf-8")

        repo.update_file(
            path=st.secrets["FILE_PATH"],
            message=f"Updated Netflix data via Streamlit ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            content=csv_bytes,
            sha=sha
        )
        st.success("✅ Changes saved to GitHub!")
    except Exception as e:
        st.error(f"Error saving file: {e}")

# ---------------------------
# MAIN APP
# ---------------------------
df, sha = load_data()

if df is not None:

    st.subheader("Search Netflix Watch History")
    query = st.text_input("Search by Title")

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

    st.subheader("Edit Netflix Data")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Save Changes to GitHub"):
        save_to_github(edited_df, sha)

else:
    st.info("No data loaded yet. Make sure your CSV has 'Title' and 'Date' columns and the GitHub secrets are set correctly.")
