import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime
from github import Github

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="📺 Netflix Watch Lookup",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------
# LOAD DATA FROM GITHUB
# ---------------------------
@st.cache_data(show_spinner=True)
def load_data():
    try:
        # Load GitHub secrets
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        file = repo.get_contents(st.secrets["FILE_PATH"])
        content = base64.b64decode(file.content).decode("utf-8")

        # Try reading CSV
        try:
            df = pd.read_csv(
                io.StringIO(content),
                sep=",",
                engine="python",
                on_bad_lines="skip",
                quotechar='"'
            )
        except Exception:
            # Fallback to tab separator if comma fails
            df = pd.read_csv(
                io.StringIO(content),
                sep="\t",
                engine="python",
                on_bad_lines="skip",
                quotechar='"'
            )

        df.columns = df.columns.str.strip()

        # Validate columns
        if "Title" not in df.columns or "Date" not in df.columns:
            st.error(f"Columns detected: {df.columns.tolist()}. Must include 'Title' and 'Date'.")
            return None, None

        # Parse dates
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        return df, file.sha

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None, None

# ---------------------------
# SAVE UPDATED DATA BACK TO GITHUB
# ---------------------------
def save_data(df, sha):
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        csv_content = df.to_csv(index=False)
        repo.update_file(
            path=st.secrets["FILE_PATH"],
            message=f"Update Netflix data via Streamlit ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})",
            content=csv_content,
            sha=sha
        )
        st.success("Data successfully updated on GitHub!")
    except Exception as e:
        st.error(f"Error saving data: {e}")

# ---------------------------
# MAIN APP
# ---------------------------
st.title("📺 Netflix Watch Lookup")

df, sha = load_data()

if df is not None:

    st.subheader("Search Your Watch History")
    query = st.text_input("Enter a title (partial matches allowed)")

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

    st.subheader("Full Watch History")
    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Save Changes to GitHub"):
        save_data(edited_df, sha)

else:
    st.info("No data loaded yet. Make sure your CSV has 'Title' and 'Date' columns and the GitHub secrets are set correctly.")
