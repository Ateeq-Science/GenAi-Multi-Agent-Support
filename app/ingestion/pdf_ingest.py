from __future__ import annotations

from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.utils.config import POLICY_DIR, VECTOR_DIR, settings


def main() -> None:
    POLICY_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(POLICY_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {POLICY_DIR}. Add policy PDFs and run again.")
        return

    loader = PyPDFDirectoryLoader(str(POLICY_DIR))
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )
    vector_store = FAISS.from_documents(splits, embeddings)
    vector_store.save_local(str(VECTOR_DIR))
    print(f"Indexed {len(splits)} chunks from {len(pdf_files)} PDF(s) into {VECTOR_DIR}")


if __name__ == "__main__":
    main()
