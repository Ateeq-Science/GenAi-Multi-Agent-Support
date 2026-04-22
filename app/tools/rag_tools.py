from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.utils.config import VECTOR_DIR, settings


def load_vector_store() -> FAISS:
    if not VECTOR_DIR.exists() or not any(VECTOR_DIR.iterdir()):
        raise FileNotFoundError(
            f"Vector store not found at {VECTOR_DIR}. Run `python -m app.ingestion.pdf_ingest` first."
        )
    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )
    return FAISS.load_local(
        folder_path=str(VECTOR_DIR),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve_policy_context(query: str, top_k: int | None = None) -> tuple[str, list[dict[str, Any]]]:
    top_k = top_k or settings.top_k
    store = load_vector_store()
    docs = store.similarity_search(query, k=top_k)
    context_parts: list[str] = []
    sources: list[dict[str, Any]] = []
    for idx, doc in enumerate(docs, start=1):
        source = Path(doc.metadata.get("source", "unknown")).name
        page = doc.metadata.get("page", "N/A")
        chunk = doc.page_content.strip()
        context_parts.append(f"[Source {idx}: {source}, page {page}]\n{chunk}")
        sources.append({"source": source, "page": page})
    return "\n\n".join(context_parts), sources
