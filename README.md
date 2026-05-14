# Deep Learning Knowledge Base — RAG Q&A System
### TIES 4911 (2026) MiniProject — Option 7: RAG with LLMs

---

## Problem Statement

Large Language Models (LLMs) such as GPT-4 or LLaMA are trained on vast corpora of text and can answer many general questions. However, they have two critical limitations:
1. **Outdated knowledge** — their training data has a cutoff date
2. **Hallucinations** — they can confidently produce plausible-sounding but incorrect information

**Our solution:** A Retrieval-Augmented Generation (RAG) system that grounds the LLM's answers in a curated domain-specific knowledge base. We build a Deep Learning Q&A assistant that answers questions about neural network architectures, object detection, Transformers, anomaly detection, and more — using only verified document sources.

---

## Architecture

```
                       INDEXING PHASE (offline)
┌──────────┐    ┌──────────┐    ┌──────────────┐    ┌────────────┐
│Documents │───►│  Chunker │───►│  Embeddings  │───►│  ChromaDB  │
│(PDF/TXT) │    │(500 chars│    │(MiniLM-L6-v2)│    │(vector DB) │
└──────────┘    │ overlap  │    │  384-dim vec │    └────────────┘
                │   50)    │    └──────────────┘
                └──────────┘

                       QUERYING PHASE (online)
┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌───────────┐
│  User    │───►│   Embedding  │───►│  Cosine    │───►│  Top-K    │
│ Question │    │  (same model)│    │ Similarity │    │  Chunks   │
└──────────┘    └──────────────┘    └────────────┘    └─────┬─────┘
                                                            │
                ┌──────────────────────────────────────────►│
                │         Augmented Prompt                  │
                ▼                                           │
┌──────────────────────────────────────────────────────────►│
│  "Answer ONLY from this context: {chunks}"  + {question}  │
└──────────────────────────────────────────────────────────►│
                │                                           │
                ▼                                           │
         ┌────────────┐                                     │
         │LLM (Ollama │◄────────────────────────────────────┘
         │ or OpenAI) │
         └─────┬──────┘
               │
               ▼
         ┌────────────┐
         │   Answer   │
         └────────────┘
```

---

## Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| Document loading | LangChain (PyPDFLoader, TextLoader) | Handles PDF + TXT in one interface |
| Text splitting | RecursiveCharacterTextSplitter | Splits on natural boundaries (paragraphs, sentences) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Small (80MB), fast, strong semantic similarity |
| Vector store | ChromaDB | Local persistent storage, no cloud needed |
| Orchestration | LangChain | Standard RAG pipeline components |
| LLM (primary) | Ollama (`llama3.2`) | Local, free, no API key |
| LLM (alternative) | OpenAI GPT-3.5/4 | Cloud-based, higher quality |
| Web UI | Gradio | Simple interactive demo |

---

## Knowledge Base

Three domain documents covering:

| File | Topics |
|------|--------|
| `deep_learning_fundamentals.txt` | ANNs, backprop, activations, regularization, optimizers |
| `transformers_and_llms.txt` | Attention, BERT, GPT, RAG, fine-tuning, vector DBs |
| `computer_vision_and_object_detection.txt` | CNNs, YOLO, Faster R-CNN, segmentation, tracking, pose |
| `anomaly_detection_and_generative_models.txt` | Autoencoders, VAE, GAN, diffusion models, anomaly datasets |

You can add your own PDFs or text files to `data/documents/` and re-run `ingest.py`.

---

## Step-by-Step Setup

### Prerequisites
- Python 3.10+
- (Optional) Ollama installed with `llama3.2` model pulled
- (Optional) OpenAI API key

### 1. Clone and navigate
```bash
cd mini-project-rag
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the LLM backend
```bash
cp .env.example .env
```
Edit `.env` and set your preferred backend:
```env
# Option A: Local LLM with Ollama (free, private)
LLM_BACKEND=ollama
OLLAMA_MODEL=llama3.2

# Option B: OpenAI (requires API key)
LLM_BACKEND=openai
OPENAI_API_KEY=sk-...

# Option C: No LLM — returns retrieved passages only
LLM_BACKEND=retrieval_only
```

**If using Ollama:**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama serve  # runs on http://localhost:11434
```

### 5. Index the documents
```bash
python ingest.py
```
This loads all documents from `data/documents/`, splits them into chunks, creates embeddings, and saves them to ChromaDB.

Expected output:
```
Found 4 document(s) to load...
  Loaded: deep_learning_fundamentals.txt
  Loaded: transformers_and_llms.txt
  ...
Split into 87 chunks
Building vector store...
Vector store saved to: ./chroma_db
Done! Indexed 87 chunks in 12.3s
```

### 6a. CLI Query Interface
```bash
python query.py
# Or ask a single question:
python query.py --question "What is self-attention?"
```

### 6b. Web UI
```bash
python app.py
# Open http://localhost:7860
```

### 6c. Jupyter Notebook Tutorial
```bash
jupyter notebook rag_tutorial.ipynb
```

---

## Example Queries

```
Q: What is Retrieval-Augmented Generation?
Q: How does YOLO detect objects?
Q: Explain the difference between VAE and GAN.
Q: What is the vanishing gradient problem?
Q: How do autoencoders detect anomalies?
Q: What metrics are used to evaluate object detection?
Q: What is LoRA fine-tuning?
```

---

## Project Structure

```
mini-project-rag/
├── app.py                  # Gradio web UI
├── ingest.py               # Document indexing script
├── query.py                # CLI query interface
├── config.py               # Centralized configuration
├── rag_tutorial.ipynb      # Step-by-step tutorial notebook
├── requirements.txt
├── .env.example            # Configuration template
├── data/
│   └── documents/          # Knowledge base (add your own files here)
│       ├── deep_learning_fundamentals.txt
│       ├── transformers_and_llms.txt
│       ├── computer_vision_and_object_detection.txt
│       └── anomaly_detection_and_generative_models.txt
├── src/
│   ├── document_processor.py  # Load + chunk documents
│   ├── vector_store.py        # ChromaDB management
│   ├── llm_interface.py       # LLM abstraction (OpenAI/Ollama/retrieval-only)
│   └── rag_pipeline.py        # High-level RAG orchestration
└── chroma_db/              # Persisted vector store (created by ingest.py)
```

---

## Use of AI

Claude Code (claude-sonnet-4-6) was used to assist in:
- Generating the boilerplate code structure and LangChain pipeline
- Writing the domain knowledge documents (Deep Learning topics)
- Creating the Gradio UI layout

All architectural decisions, integration design, and project structure were designed by the student.

---

## References

- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* arXiv:2005.11401
- Vaswani et al. (2017). *Attention Is All You Need.* NeurIPS 2017.
- LangChain Documentation: https://python.langchain.com
- ChromaDB Documentation: https://docs.trychroma.com
- Sentence Transformers: https://sbert.net
- Ollama: https://ollama.ai
