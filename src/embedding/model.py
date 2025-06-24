# model.py
from sentence_transformers import SentenceTransformer

_embedder = None

def load_embedder(model_name: str = "all-MiniLM-L6-v2"):
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(model_name)
    return _embedder

def get_embedder():
    return load_embedder()
