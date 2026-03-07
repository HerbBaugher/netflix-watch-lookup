import streamlit as st
import pandas as pd
import io
from datetime import datetime
from odf.opendocument import load
from odf.text import P

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Netflix Watch Lookup",
    page_icon="🎬",
    layout="centered"
)

# ---------------------------
# CUSTOM CSS FOR NICER UI
# ---------------------------
st.markdown("""
<style>
/* Center the main container */
.main > div {
    max-width: 700px;
    margin: auto;
}

/* Input styling */
input[type="text"] {
    border-radius: 8px !important;
}

/* Card style for results */
.result-card {
    background: #f8f9fa;
    padding: 18px 22px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-top: 15px;
}

/* Title styling */
h1 {
    text-align: center;
    font-weight: 700;
}

/* Date bullets */
.date-item {
    padding-left: 10px;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# READ ODT FILE
# ---------------------------
def read_odt(file):
    textdoc = load(file)
    lines = []
    for p in textdoc.getElementsByType(P):
        lines.append(str(p))
    csv_text = "\n".join(lines)
    return pd.read_csv(io.StringIO(csv_text))

# ---------------------------
# LOAD DATAFRAME
# ---------------------------
def load_dataframe(uploaded_file):

    if uploaded_file.name.lower().endswith(".odt"):
        df = read_odt(uploaded_file)
    else:
        df = pd.read_csv(
            uploaded_file,
            encoding="latin1",
            engine="python",
            on_bad_lines="skip"
        )

    df.columns = (
        df.columns
        .str.strip()
        .str.replace('"', '', regex=False)
        .str.replace("'", "", regex=False)
        .str.replace("ï»¿", "", regex=False)
    )

    if "Title" not in df.columns or "Date" not in df.columns:
        st.error(f"Columns detected: {df.columns.tolist()}\nFile must contain Title and Date")
        return None

    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%y", errors="coerce")
    df = df.dropna(subset=["Date"])

    return df

# ---------------------------
# UI
# ---------------------------
st.title("🎬 Netflix Watch Lookup")

st.write("Upload your Netflix viewing history and instantly search when you watched any title.")

uploaded_file = st.file_uploader("Upload Netflix history file", type=["csv", "odt"])

df = None

if uploaded_file:
    df = load_dataframe(uploaded_file)

if df is not None:

    query = st.text_input("Search for a title")

    if query:

        matches = df[df["Title"].str.lower().str.contains(query.lower(), na=False)]

        if matches.empty:
            st.warning(f"No watch history found for **{query}**.")
        else:
            latest = matches["Date"].max()

            st.markdown(f"""
            <div class="result-card">
                <h3>Results for: <strong>{query}</strong></h3>
                <p><strong>Most recent watch:</strong> {latest.date()}</p>
                <p><strong>Total times watched:</strong> {len(matches)}</p>
                <hr>
                <p><strong>All dates watched:</strong></p>
            </div>
            """, unsafe_allow_html=True)

            for date in matches["Date"].sort_values():
                st.markdown(f"<div class='date-item'>• {date.date()}</div>", unsafe_allow_html=True)

