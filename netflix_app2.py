import streamlit as st
import pandas as pd
import base64
from github import Github

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="📺 Netflix Watch Lookup", layout="centered")

st.title("📺 Netflix Watch Lookup")

# ---------------------------
# GITHUB SETTINGS
# ---------------------------
# Make sure your GitHub token is in secrets.toml
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    REPO_NAME = st.secrets["REPO_NAME"]
    FILE_PATH = st.secrets["FILE_PATH"]
except Exception:
    g = None
    st.warning("GitHub secrets not set. Upload a file manually.")

# ---------------------------
# PARSER FOR SPACE-SEPARATED TXT
# ---------------------------
def parse_netflix_txt(file_content):
    """
    Parse Netflix_txt.txt even if space separated or multi-line titles exist.
    Returns a DataFrame with 'Title' and 'Date'.
    """
    lines = file_content.splitlines()
    data = []
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try splitting last word as date
        parts = line.rsplit(maxsplit=1)
        if len(parts) == 2:
            title_part, date_part = parts
            try:
                date = pd.to_datetime(date_part, errors="raise", dayfirst=False)
                full_title = " ".join(buffer + [title_part]) if buffer else title_part
                data.append({"Title": full_title, "Date": date})
                buffer = []
            except Exception:
                buffer.append(line)
        else:
            buffer.append(line)

    return pd.DataFrame(data)

# ---------------------------
# LOAD DATAFRAME
# ---------------------------
df = None

# Option 1: Load directly from GitHub
if g:
    try:
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        content = base64.b64decode(file.content).decode("utf-8")
        df = parse_netflix_txt(content)
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")

# Option 2: Upload manually
uploaded_file = st.file_uploader("Or upload your Netflix history file", type=["txt", "csv"])
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    df = parse_netflix_txt(content)

# ---------------------------
# DISPLAY DATA
# ---------------------------
if df is not None and not df.empty:
    st.write(f"ROWS LOADED: {len(df)}")

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
else:
    st.info("No data loaded yet. Make sure your file has the correct format.")
