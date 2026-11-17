"""
Sentence-embedding reference ranking (A1). Embeddings are cached on disk under
out/cache/ keyed by model name and text, so reruns don't recompute them.
"""

import hashlib
import json

import numpy as np

from experiments.common import paths

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_MODELS = {}


def _model(name):
    if name not in _MODELS:
        from sentence_transformers import SentenceTransformer  # heavy import, only when needed
        _MODELS[name] = SentenceTransformer(name, device="cpu")
    return _MODELS[name]


def embed(texts, model=DEFAULT_MODEL):
    texts = list(texts)
    key = hashlib.sha1(json.dumps([model, texts]).encode("utf-8")).hexdigest()[:16]
    paths.ensure_out()
    cache = paths.CACHE_DIR / f"emb_{key}.npy"
    if cache.exists():
        return np.load(cache)
    vecs = _model(model).encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    vecs = np.asarray(vecs, dtype=np.float32)
    np.save(cache, vecs)
    return vecs


def cosine_rect(D, E, model=DEFAULT_MODEL):
    """(|D| x |E|) cosine similarity (embeddings are L2-normalised)."""
    return embed(D, model) @ embed(E, model).T
