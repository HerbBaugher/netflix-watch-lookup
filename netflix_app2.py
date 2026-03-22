import streamlit as st
import pandas as pd
import base64
import io
from github import Github
from datetime import datetime

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Netflix Watch Lookup", layout="wide")
st.title("📺 Netflix Watch Lookup")

# ---------------------------
# LOAD DATA FROM GITHUB
# ---------------------------
@st.cache_data(show_spinner=True)
def load_data():
    """Load Netflix_txt.txt from GitHub using secrets."""
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        file_path = st.secrets["FILE_PATH"]

        file_content = repo.get_contents(file_path)
        content = base64.b64decode(file_content.content).decode("utf-8")

        # Load CSV
        df = pd.read_csv(io.StringIO(content), sep=",", engine="python", on_bad_lines="skip")

        # Clean column names
        df.columns = (
            df.columns
            .str.strip()
            .str.replace('"', '', regex=False)
            .str.replace("'", "", regex=False)
            .str.replace("ï»¿", "", regex=False)
        )

        # Ensure required columns
        if "Title" not in df.columns or "Date" not in df.columns:
            st.error(f"Columns detected: {df.columns.tolist()}. Must include 'Title' and 'Date'.")
            return None, None

        # Convert Date to datetime
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        return df, file_content.sha

    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return None, None


df, sha = load_data()

if df is not None:
    st.subheader("Edit Netflix Data")
    edited_df = st.data_editor(df, num_rows="dynamic")

    # ---------------------------
    # SAVE BACK TO GITHUB
    # ---------------------------
    if st.button("Save Changes to GitHub"):
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo(st.secrets["REPO_NAME"])
            csv_bytes = edited_df.to_csv(index=False).encode("utf-8")

            repo.update_file(
                path=st.secrets["FILE_PATH"],
                message="Updated Netflix data via Streamlit",
                content=csv_bytes,
                sha=sha
            )
            st.success("✅ Changes saved to GitHub!")

        except Exception as e:
            st.error(f"Failed to save changes: {e}")

    # ---------------------------
    # SEARCH & DISPLAY
    # ---------------------------
    st.subheader("Search Netflix Watch History")
    query = st.text_input("Search by Title")

    if query:
        matches = df[df["Title"].str.lower().str.contains(query.lower(), na=False)]
        if matches.empty:
            st.warning(f"No watch history found for **{query}**.")
        else:
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

else:
    st.info("No data loaded yet.")
