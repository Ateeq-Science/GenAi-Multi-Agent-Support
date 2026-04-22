from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.utils.config import VECTOR_STORE_DIR, settings


def load_vector_store() -> FAISS:
    vector_dir = Path(VECTOR_STORE_DIR)
    if not vector_dir.exists():
        raise FileNotFoundError(
            f"Vector store not found at {vector_dir}. Run: python -m app.ingestion.pdf_ingest"
        )

    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    return FAISS.load_local(
        str(vector_dir),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve_policy_context(query: str, k: int = 4) -> Tuple[str, List[dict]]:
    store = load_vector_store()
    docs: List[Document] = store.similarity_search(query, k=k)

    if not docs:
        return "No relevant policy context found.", []

    context = "\n\n".join(doc.page_content for doc in docs)
    sources = []

    for doc in docs:
        metadata = doc.metadata or {}
        sources.append(
            {
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page", "N/A"),
            }
        )

    return context, sources