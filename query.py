"""
query.py — CLI interface to query the RAG system interactively.

Usage:
    python query.py
    python query.py --question "What is backpropagation?"
    python query.py --question "How does YOLO work?" --top-k 5
"""

import argparse
import sys

from src.rag_pipeline import RAGPipeline


EXAMPLE_QUESTIONS = [
    "What is a Transformer and how does self-attention work?",
    "Explain the difference between YOLO and Faster R-CNN.",
    "What is Retrieval-Augmented Generation (RAG)?",
    "How do autoencoders detect anomalies?",
    "What is the vanishing gradient problem and how is it solved?",
    "What is LoRA fine-tuning?",
    "How does the YOLO object detection algorithm work?",
    "What is the difference between VAE and GAN?",
]


def print_result(result: dict):
    print("\n" + "=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(result["answer"])
    print("\n" + "-" * 60)
    print(f"Sources: {', '.join(result['sources'])}")
    if result.get("retrieved_docs"):
        print(f"Retrieved {len(result['retrieved_docs'])} chunk(s)")
        for i, (doc, score) in enumerate(result["retrieved_docs"], 1):
            src = doc.metadata.get("source_file", "?")
            print(f"  [{i}] {src} — relevance: {score:.3f}")
    print("=" * 60)


def interactive_mode(pipeline: RAGPipeline):
    print("\n" + "=" * 60)
    print("Deep Learning Knowledge Base — Interactive Q&A")
    print("Type 'quit' or 'exit' to stop. Type 'examples' for sample questions.")
    print("=" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if question.lower() == "examples":
            print("\nExample questions:")
            for i, q in enumerate(EXAMPLE_QUESTIONS, 1):
                print(f"  {i}. {q}")
            continue

        if not question:
            continue

        result = pipeline.query(question)
        print_result(result)


def main():
    parser = argparse.ArgumentParser(description="Query the Deep Learning RAG knowledge base.")
    parser.add_argument("--question", "-q", type=str, help="Ask a single question and exit.")
    parser.add_argument("--top-k", type=int, default=None, help="Number of chunks to retrieve.")
    args = parser.parse_args()

    pipeline = RAGPipeline()
    pipeline.initialize()

    if args.question:
        result = pipeline.query(args.question, top_k=args.top_k)
        print_result(result)
    else:
        interactive_mode(pipeline)


if __name__ == "__main__":
    main()
