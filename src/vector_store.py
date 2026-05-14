"""
Vector store management using ChromaDB.
Handles creating, loading, and querying the vector database.
"""

import os
from typing import List, Tuple

import chromadb
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import config


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return a HuggingFace sentence-transformers embedding model.
    all-MiniLM-L6-v2 is fast, small (~80MB), and produces strong embeddings
    for semantic similarity tasks.
    """
    print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return embeddings


def build_vector_store(chunks: List[Document]) -> Chroma:
    """
    Embed document chunks and persist them in ChromaDB.
    Overwrites any existing collection with the same name.
    """
    embeddings = get_embeddings()

    # Remove old collection if it exists to rebuild fresh
    if os.path.exists(config.CHROMA_DB_PATH):
        client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        try:
            client.delete_collection(config.CHROMA_COLLECTION)
            print(f"Deleted existing collection: {config.CHROMA_COLLECTION}")
        except Exception:
            pass

    print(f"Building vector store with {len(chunks)} chunks...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=config.CHROMA_DB_PATH,
        collection_name=config.CHROMA_COLLECTION,
    )
    print(f"Vector store saved to: {config.CHROMA_DB_PATH}")
    return vector_store


def load_vector_store() -> Chroma:
    """
    Load an existing ChromaDB vector store from disk.
    Raises FileNotFoundError if the store does not exist yet.
    """
    if not os.path.exists(config.CHROMA_DB_PATH):
        raise FileNotFoundError(
            f"Vector store not found at {config.CHROMA_DB_PATH}. "
            "Run ingest.py first to build the index."
        )
    embeddings = get_embeddings()
    vector_store = Chroma(
        persist_directory=config.CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=config.CHROMA_COLLECTION,
    )
    count = vector_store._collection.count()
    print(f"Loaded vector store: {count} chunk(s) indexed.")
    return vector_store


def retrieve(vector_store: Chroma, query: str, k: int = None) -> List[Tuple[Document, float]]:
    """
    Retrieve the top-k most relevant chunks for a query.
    Returns list of (Document, relevance_score) tuples.
    Score is cosine similarity (0-1, higher = more relevant).
    """
    k = k or config.TOP_K_RESULTS
    results = vector_store.similarity_search_with_relevance_scores(query, k=k)
    return results
