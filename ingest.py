"""
ingest.py — Index documents into the vector store.

Run this script once (or whenever you add/update documents):
    python ingest.py
    python ingest.py --docs path/to/your/docs
"""

import argparse
import sys
import time

from src.document_processor import load_and_split
from src.vector_store import build_vector_store


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG vector store.")
    parser.add_argument(
        "--docs",
        type=str,
        default=None,
        help="Path to documents directory (default: ./data/documents)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("RAG Document Ingestion")
    print("=" * 60)

    start = time.time()

    try:
        # Step 1: Load and chunk documents
        print("\n[Step 1] Loading and splitting documents...")
        chunks = load_and_split(args.docs)

        # Step 2: Build vector store
        print("\n[Step 2] Building vector store (embedding chunks)...")
        vector_store = build_vector_store(chunks)

        elapsed = time.time() - start
        print(f"\nDone! Indexed {len(chunks)} chunks in {elapsed:.1f}s")
        print("You can now run: python query.py  or  python app.py")

    except FileNotFoundError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
