from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.config import POLICY_DIR, VECTOR_STORE_DIR, settings


def main() -> None:
    policy_dir = Path(POLICY_DIR)
    vector_dir = Path(VECTOR_STORE_DIR)

    if not policy_dir.exists():
        raise FileNotFoundError(f"Policy directory not found: {policy_dir}")

    pdf_files = list(policy_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {policy_dir}. Add at least one policy PDF first."
        )

    documents = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)

    vector_dir.mkdir(parents=True, exist_ok=True)
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(vector_dir))

    print(f"Ingested {len(pdf_files)} PDF(s) and saved vector store to {vector_dir}")


if __name__ == "__main__":
    main()