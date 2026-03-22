import streamlit as st
import pandas as pd
import base64
from github import Github
from io import StringIO

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="📺 Netflix Watch Lookup", layout="centered")
st.title("📺 Netflix Watch Lookup (Editable)")

# ---------------------------
# GITHUB SETTINGS
# ---------------------------
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    REPO_NAME = st.secrets["REPO_NAME"]
    FILE_PATH = st.secrets["FILE_PATH"]
except Exception:
    g = None
    st.warning("GitHub secrets not set. Upload file manually for editing.")

# ---------------------------
# PARSER FOR MULTI-LINE TXT
# ---------------------------
def parse_netflix_txt(file_content):
    lines = file_content.splitlines()
    data = []
    buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.rsplit(maxsplit=1)
        if len(parts) == 2:
            title_part, date_part = parts
            try:
                date = pd.to_datetime(date_part, errors="raise", dayfirst=False)
                full_title = " ".join(buffer + [title_part]) if buffer else title_part
                data.append({"Title": full_title, "Date": date.date()})
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
if g:
    try:
        repo = g.get_repo(REPO_NAME)
        file = repo.get_contents(FILE_PATH)
        content = base64.b64decode(file.content).decode("utf-8")
        df = parse_netflix_txt(content)
    except Exception as e:
        st.error(f"Error loading file from GitHub: {e}")

uploaded_file = st.file_uploader("Or upload your Netflix history file", type=["txt", "csv"])
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    df = parse_netflix_txt(content)

# ---------------------------
# EDITABLE TABLE
# ---------------------------
if df is not None and not df.empty:
    st.subheader("Your Netflix Watch History")
    edited_df = st.experimental_data_editor(df, num_rows="dynamic")

    # ---------------------------
    # SAVE BACK TO GITHUB
    # ---------------------------
    if st.button("Save to GitHub") and g:
        csv_buffer = StringIO()
        # Convert back to your space-separated format
        for _, row in edited_df.iterrows():
            csv_buffer.write(f"{row['Title']} {row['Date']}\n")
        new_content = csv_buffer.getvalue()

        # Update the file in GitHub
        try:
            file = repo.get_contents(FILE_PATH)
            repo.update_file(
                path=FILE_PATH,
                message="Update Netflix watch history via Streamlit app",
                content=new_content,
                sha=file.sha
            )
            st.success("✅ Netflix_txt.txt updated in GitHub!")
        except Exception as e:
            st.error(f"Failed to update GitHub: {e}")

else:
    st.info("No data loaded yet. Make sure your file has correct format.")
