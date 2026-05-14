"""
Main RAG pipeline: ties together retrieval and generation.
"""

from typing import Optional

from src.vector_store import load_vector_store, retrieve
from src.llm_interface import get_llm, generate_answer

import config


class RAGPipeline:
    """
    High-level RAG pipeline.

    Usage:
        pipeline = RAGPipeline()
        result = pipeline.query("What is a Transformer?")
        print(result["answer"])
    """

    def __init__(self):
        self.vector_store = None
        self.llm = None
        self._initialized = False

    def initialize(self):
        """Load the vector store and LLM. Call once before querying."""
        if self._initialized:
            return
        print("Initializing RAG pipeline...")
        self.vector_store = load_vector_store()
        self.llm = get_llm()
        self._initialized = True
        print("RAG pipeline ready.")

    def query(self, question: str, top_k: Optional[int] = None) -> dict:
        """
        Answer a question using RAG.

        Steps:
          1. Embed the question.
          2. Retrieve the top-k most relevant document chunks.
          3. Augment the LLM prompt with retrieved context.
          4. Generate and return the answer.

        Returns a dict with keys: answer, sources, context, retrieved_docs.
        """
        if not self._initialized:
            self.initialize()

        if not question.strip():
            return {"answer": "Please enter a question.", "sources": [], "context": "", "retrieved_docs": []}

        # Step 1 & 2: Retrieve
        retrieved_docs = retrieve(self.vector_store, question, k=top_k or config.TOP_K_RESULTS)

        if not retrieved_docs:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "sources": [],
                "context": "",
                "retrieved_docs": [],
            }

        # Step 3 & 4: Generate
        result = generate_answer(question, retrieved_docs, self.llm)
        result["retrieved_docs"] = retrieved_docs
        return result
