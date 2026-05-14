"""
LLM abstraction layer.
Supports OpenAI, Ollama (local), and retrieval-only (no LLM) modes.
"""

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

import config


RAG_PROMPT_TEMPLATE = """\
You are an expert assistant in Deep Learning and Artificial Intelligence.
Use ONLY the context provided below to answer the question.
If the answer cannot be found in the context, say "I don't have enough information in my knowledge base to answer this question."
Do not make up information or use knowledge outside the provided context.
Be concise, accurate, and helpful.

Context:
{context}

Question: {question}

Answer:"""


def get_llm() -> BaseLanguageModel:
    """
    Return an LLM instance based on the configured backend.
    Raises ImportError or ConnectionError with helpful messages if setup is needed.
    """
    backend = config.LLM_BACKEND.lower()

    if backend == "openai":
        from langchain_openai import ChatOpenAI
        if not config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. Add it to your .env file or "
                "set LLM_BACKEND=ollama or LLM_BACKEND=retrieval_only."
            )
        print(f"Using OpenAI model: {config.OPENAI_MODEL}")
        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.2,
        )

    elif backend == "ollama":
        from langchain_community.llms import Ollama
        print(f"Using Ollama model: {config.OLLAMA_MODEL} at {config.OLLAMA_BASE_URL}")
        return Ollama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.2,
        )

    elif backend == "retrieval_only":
        print("Using retrieval-only mode (no LLM generation).")
        return None

    else:
        raise ValueError(
            f"Unknown LLM_BACKEND: '{backend}'. "
            "Choose from: openai, ollama, retrieval_only."
        )


def get_prompt() -> ChatPromptTemplate:
    """Return the RAG prompt template."""
    return ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)


def format_context(retrieved_docs) -> str:
    """Format retrieved document chunks into a single context string."""
    parts = []
    for i, (doc, score) in enumerate(retrieved_docs, 1):
        source = doc.metadata.get("source_file", "unknown")
        parts.append(
            f"[Source {i} - {source} (relevance: {score:.2f})]:\n{doc.page_content}"
        )
    return "\n\n".join(parts)


def generate_answer(question: str, retrieved_docs, llm=None) -> dict:
    """
    Generate an answer given a question and retrieved document chunks.

    Returns a dict with:
      - answer: the generated (or assembled) answer
      - sources: list of source file names
      - context: the raw context passed to the LLM
    """
    context = format_context(retrieved_docs)
    sources = list({doc.metadata.get("source_file", "unknown") for doc, _ in retrieved_docs})

    if llm is None or config.LLM_BACKEND == "retrieval_only":
        # Return retrieved chunks as the "answer" without LLM synthesis
        answer = (
            "Retrieval-only mode — here are the most relevant passages from the knowledge base:\n\n"
            + context
        )
    else:
        prompt = get_prompt()
        chain = prompt | llm
        response = chain.invoke({"context": context, "question": question})
        # Handle both string and AIMessage responses
        answer = response.content if hasattr(response, "content") else str(response)

    return {
        "answer": answer,
        "sources": sources,
        "context": context,
    }
