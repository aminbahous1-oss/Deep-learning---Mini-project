import os
from dotenv import load_dotenv

load_dotenv()

# LLM Backend
LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama")  # "openai", "ollama", "retrieval_only"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Vector store
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "rag_knowledge_base")

# RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 4))

# Documents folder
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", "./data/documents")
