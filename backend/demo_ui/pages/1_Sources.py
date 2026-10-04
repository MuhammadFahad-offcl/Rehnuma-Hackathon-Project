"""Sources page: every value, its link, the date it was verified and Official/Unofficial."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _bootstrap  # noqa: E402,F401

from app.sources import build_sources  # noqa: E402
from data.loader import is_fixture, load_data  # noqa: E402

st.set_page_config(page_title="Sources — Rehnuma", page_icon="🔗", layout="wide")
st.title("Where every number comes from")

data = load_data()
if is_fixture(data):
    st.warning("**Demo data.** These rows are placeholders until the verified dataset is added.")

link = {"Source": st.column_config.LinkColumn("Source", display_text="open source")}
for university in build_sources(data):
    st.subheader(f"{university['universityName']} — {university['programName']}")
    rows = [
        {
            "Field": row["label"],
            "Value": row["display"],
            "Source": row["source"]["sourceUrl"] if row["source"] else None,
            "Verified": row["source"]["verifiedOn"] if row["source"] else "",
            "Flag": row["source"]["confidence"].capitalize() if row["source"] else "",
        }
        for row in university["rows"]
    ]
    st.dataframe(rows, column_config=link, hide_index=True, width="stretch")
