import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Optional ODT support
try:
    from odf.opendocument import load
    from odf.text import P
    ODT_ENABLED = True
except:
    ODT_ENABLED = False


# ---------------------------
# READ ODT FILE
# ---------------------------
def read_odt(file):
    if not ODT_ENABLED:
        st.error("ODT support not installed. Add 'odfpy' to requirements.txt")
        return None

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

    name = uploaded_file.name.lower()

    if name.endswith(".odt"):
        df = read_odt(uploaded_file)
    elif name.endswith(".txt"):
        df = pd.read_csv(uploaded_file, sep=",", engine="python", on_bad_lines="skip")
    else:
        df = pd.read_csv(uploaded_file, engine="python", on_bad_lines="skip")

    if df is None:
        return None

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace('"', '', regex=False)
        .str.replace("'", "", regex=False)
        .str.replace("ï»¿", "", regex=False)
    )

    # Validate required columns
    if "Title" not in df.columns or "Date" not in df.columns:
        st.error(f"Columns detected: {df.columns.tolist()}\nFile must contain Title and Date")
        return None

    # Parse Netflix date format
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    return df


# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("📺 Netflix Watch Lookup")

uploaded_file = st.file_uploader("Upload Netflix history file", type=["csv", "txt", "odt"])

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

            st.subheader("Matching Titles")

            grouped = matches.groupby("Title")

            for title, group in grouped:

                latest = group["Date"].max()

                # Title (full, no truncation)
                st.markdown(f"### {title}")

                st.write(f"**Times Watched:** {len(group)}")
                st.write(f"**Most Recent Watch:** {latest.date()}")

                st.write("**All Dates Watched:**")
                for date in group["Date"].sort_values():
                    st.write(f"- {date.date()}")

                st.markdown("---")

