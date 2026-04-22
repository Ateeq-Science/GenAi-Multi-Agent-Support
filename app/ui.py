from __future__ import annotations

import shutil
from pathlib import Path

import streamlit as st

from app.graph import run_query
from app.ingestion.pdf_ingest import main as ingest_pdfs
from app.utils.config import POLICY_DIR

st.set_page_config(page_title="GenAI Multi-Agent Support Assistant", page_icon="🤖", layout="wide")

st.title("🤖 Generative AI Multi-Agent Support Assistant")
st.caption("Natural language support assistant over structured customer data and unstructured policy PDFs")

with st.sidebar:
    st.header("Policy Document Upload")
    uploads = st.file_uploader(
        "Upload one or more policy PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )
    if st.button("Save and Index PDFs"):
        POLICY_DIR.mkdir(parents=True, exist_ok=True)
        for uploaded in uploads or []:
            target = POLICY_DIR / uploaded.name
            with open(target, "wb") as f:
                f.write(uploaded.read())
        ingest_pdfs()
        st.success("PDFs indexed successfully.")

    st.markdown("---")
    st.subheader("Suggested Questions")
    st.markdown("- What is the current refund policy?")
    st.markdown("- Give me a quick overview of customer Ema’s profile and past support ticket details.")
    st.markdown("- Based on the refund policy, is Ema likely eligible for a refund?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            with st.expander("Details"):
                st.json(msg["meta"])

user_input = st.chat_input("Ask about policy documents or customer support data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_query(user_input)
                answer = result.get("final_answer", "No answer generated.")
                st.markdown(answer)
                meta = {
                    "route": result.get("route"),
                    "sources": result.get("sources", []),
                }
                if meta["sources"]:
                    with st.expander("Sources"):
                        st.json(meta["sources"])
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "meta": meta}
                )
            except Exception as exc:
                error_msg = f"Error: {exc}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
