"""
app.py — Gradio web UI for the Deep Learning RAG system.

Run with:
    python app.py
Then open http://localhost:7860 in your browser.
"""

import gradio as gr
from src.rag_pipeline import RAGPipeline

# --- Initialize pipeline (shared across requests) ---
pipeline = RAGPipeline()

EXAMPLE_QUESTIONS = [
    "What is a Transformer and how does self-attention work?",
    "Explain how YOLO detects objects in an image.",
    "What is Retrieval-Augmented Generation (RAG) and what are its benefits?",
    "How do Variational Autoencoders detect anomalies?",
    "What is the difference between instance segmentation and semantic segmentation?",
    "What is LoRA fine-tuning and why is it efficient?",
    "Explain backpropagation and gradient descent.",
    "What are diffusion models and how do they compare to GANs?",
    "What is the vanishing gradient problem?",
    "What metrics are used to evaluate object detection models?",
]

CSS = """
.answer-box { background: #1e1e2e; border-radius: 8px; padding: 16px; }
.source-box  { background: #2a2a3e; border-radius: 6px; padding: 10px; font-size: 0.85em; }
footer { display: none !important; }
"""


def query_rag(question: str, top_k: int, show_context: bool):
    """Called by Gradio on each submission."""
    if not question.strip():
        return "Please enter a question.", "", ""

    try:
        if not pipeline._initialized:
            pipeline.initialize()
        result = pipeline.query(question.strip(), top_k=int(top_k))
    except FileNotFoundError:
        return (
            "Vector store not found. Please run `python ingest.py` first to index the documents.",
            "",
            "",
        )
    except Exception as e:
        return f"Error: {e}", "", ""

    answer = result["answer"]
    sources_md = "**Sources used:**\n" + "\n".join(
        f"- `{s}`" for s in result["sources"]
    )

    # Build retrieved chunks display
    chunks_md = ""
    if result.get("retrieved_docs"):
        lines = [f"### Retrieved {len(result['retrieved_docs'])} Chunk(s)\n"]
        for i, (doc, score) in enumerate(result["retrieved_docs"], 1):
            src = doc.metadata.get("source_file", "unknown")
            preview = doc.page_content[:300].replace("\n", " ")
            lines.append(
                f"**Chunk {i}** — `{src}` (relevance: `{score:.3f}`)\n"
                f"> {preview}...\n"
            )
        chunks_md = "\n".join(lines)

    context_display = result["context"] if show_context else ""

    return answer, sources_md + ("\n\n" + chunks_md if chunks_md else ""), context_display


def build_ui():
    with gr.Blocks(title="Deep Learning RAG Q&A", css=CSS, theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
# Deep Learning Knowledge Base — RAG Q&A System
**Option 7 — TIES 4911 (2026) Mini Project**

Ask any question about Deep Learning, Computer Vision, Transformers, LLMs, Anomaly Detection, and more.
The system retrieves relevant passages from the knowledge base and uses an LLM to generate a grounded answer.
        """)

        with gr.Row():
            with gr.Column(scale=2):
                question_input = gr.Textbox(
                    label="Your Question",
                    placeholder="e.g. How does the attention mechanism work in Transformers?",
                    lines=3,
                )
                with gr.Row():
                    top_k_slider = gr.Slider(
                        minimum=1, maximum=8, value=4, step=1,
                        label="Top-K chunks to retrieve",
                    )
                    show_context_cb = gr.Checkbox(
                        label="Show full context passed to LLM", value=False
                    )
                submit_btn = gr.Button("Ask", variant="primary", size="lg")

                gr.Markdown("### Example Questions")
                example_component = gr.Examples(
                    examples=[[q] for q in EXAMPLE_QUESTIONS],
                    inputs=question_input,
                )

            with gr.Column(scale=3):
                answer_output = gr.Textbox(
                    label="Answer",
                    lines=12,
                    interactive=False,
                    elem_classes=["answer-box"],
                )
                sources_output = gr.Markdown(label="Sources & Retrieved Chunks")
                context_output = gr.Textbox(
                    label="Full Context (debug)",
                    lines=8,
                    interactive=False,
                    visible=True,
                )

        submit_btn.click(
            fn=query_rag,
            inputs=[question_input, top_k_slider, show_context_cb],
            outputs=[answer_output, sources_output, context_output],
        )
        question_input.submit(
            fn=query_rag,
            inputs=[question_input, top_k_slider, show_context_cb],
            outputs=[answer_output, sources_output, context_output],
        )

        gr.Markdown("""
---
**How it works:** Documents → Chunked → Embedded (sentence-transformers) → ChromaDB →
Query embedded → Top-K cosine similarity → LLM (Ollama/OpenAI) generates answer from context.
        """)

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
