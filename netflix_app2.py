import streamlit as st
import pandas as pd
import io
import base64
from github import Github
from odf.opendocument import load
from odf.text import P

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(
    page_title="Netflix Data Editor",
    layout="wide"
)
st.title("📺 Netflix Watch Lookup & Editor")
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
# ---------------------------
# READ ODT FILE (optional)
# ---------------------------
def read_odt(file):
    textdoc = load(file)
    lines = []
    for p in textdoc.getElementsByType(P):
        lines.append(str(p))
    csv_text = "\n".join(lines)
    return pd.read_csv(io.StringIO(csv_text))

# ---------------------------
# LOAD DATA FROM GITHUB
# ---------------------------
@st.cache_data
def load_data():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        file = repo.get_contents(st.secrets["FILE_PATH"])
        content = base64.b64decode(file.content)

        # Detect file type
        if st.secrets["FILE_PATH"].lower().endswith(".odt"):
            df = read_odt(io.BytesIO(content))
        elif st.secrets["FILE_PATH"].lower().endswith(".txt"):
            df = pd.read_csv(io.StringIO(content.decode("utf-8")), sep=",", engine="python", on_bad_lines="skip")
        else:
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))

        # Clean column names
        df.columns = (
            df.columns
            .str.strip()
            .str.replace('"', '', regex=False)
            .str.replace("'", "", regex=False)
            .str.replace("ï»¿", "", regex=False)
        )

        # Parse Netflix date column
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])

        return df, file.sha

    except Exception as e:
        st.error(f"Error loading data from GitHub: {e}")
        return None, None

# ---------------------------
# LOAD DATA
# ---------------------------
df, sha = load_data()

if df is not None:
    st.subheader("Edit Netflix Data")
    edited_df = st.data_editor(df, num_rows="dynamic")

    # ---------------------------
    # SAVE BACK TO GITHUB
    # ---------------------------
    if st.button("Save Changes"):
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
            st.success("Changes saved to GitHub!")
        except Exception as e:
            st.error(f"Error saving file: {e}")
else:
    st.info("No data loaded. Check your GitHub token, repo, or file path in secrets.toml")
