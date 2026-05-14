"""
Document loading and chunking for the RAG pipeline.
Supports PDF, TXT, and Markdown files.
"""

import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)

import config


def load_documents(directory: str = None) -> List[Document]:
    """
    Load all supported documents from a directory.
    Supports .pdf, .txt, and .md files.
    """
    directory = directory or config.DOCUMENTS_DIR
    docs: List[Document] = []

    if not os.path.exists(directory):
        raise FileNotFoundError(f"Documents directory not found: {directory}")

    supported = {".pdf", ".txt", ".md"}
    files = [f for f in Path(directory).rglob("*") if f.suffix.lower() in supported]

    if not files:
        raise ValueError(f"No supported documents found in {directory}")

    print(f"Found {len(files)} document(s) to load...")

    for file_path in files:
        try:
            ext = file_path.suffix.lower()
            if ext == ".pdf":
                loader = PyPDFLoader(str(file_path))
            else:
                loader = TextLoader(str(file_path), encoding="utf-8")

            loaded = loader.load()
            # Attach filename metadata for citation
            for doc in loaded:
                doc.metadata["source_file"] = file_path.name
            docs.extend(loaded)
            print(f"  Loaded: {file_path.name} ({len(loaded)} chunk(s))")

        except Exception as e:
            print(f"  Warning: Could not load {file_path.name}: {e}")

    print(f"Total documents loaded: {len(docs)}")
    return docs


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks for embedding.
    Uses RecursiveCharacterTextSplitter which tries to split on
    paragraph and sentence boundaries before character splits.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks "
          f"(chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})")
    return chunks


def load_and_split(directory: str = None) -> List[Document]:
    """Convenience function: load + split in one call."""
    docs = load_documents(directory)
    return split_documents(docs)
