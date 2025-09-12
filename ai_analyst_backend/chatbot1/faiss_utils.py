# faiss_utils.py
import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any, Optional
 
FAISS_INDEX_PATH = "faiss_index.bin"
FAISS_META_PATH = "faiss_meta.pkl"
 
 
class FaissIndex:
    def __init__(self, dim: int = 384, use_ivf: bool = False, nlist: int = 100):
        """
        :param dim: Embedding dimension
        :param use_ivf: Use IVF (approximate search) if True, else Flat index
        :param nlist: Number of clusters for IVF
        """
        self.dim = dim
        self.metadata: List[Dict[str, Any]] = []
 
        if use_ivf:
            quantizer = faiss.IndexFlatIP(dim)  # inner product quantizer
            self.index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
        else:
            self.index = faiss.IndexFlatIP(dim)  # exact search
 
        # Try loading existing index + metadata
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(FAISS_META_PATH):
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(FAISS_META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
 
    def _normalize(self, embeddings: np.ndarray) -> np.ndarray:
        """L2 normalize embeddings for cosine similarity."""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
        return embeddings / norms
 
    def save(self):
        """Save FAISS index + metadata."""
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(FAISS_META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)
 
    def add(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]]):
        """Add vectors + metadata to index."""
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
 
        embeddings = self._normalize(embeddings).astype("float32")
 
        if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
            print("⚠️ Training FAISS IVF index...")
            self.index.train(embeddings)
 
        self.index.add(embeddings)
        self.metadata.extend(metadatas)
        self.save()
 
    def search(
        self,
        query_emb: np.ndarray,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search nearest neighbors with optional metadata filtering."""
        if query_emb.ndim == 1:
            query_emb = query_emb.reshape(1, -1)
 
        query_emb = self._normalize(query_emb).astype("float32")
        sims, idxs = self.index.search(query_emb, top_k * 3)  # fetch more, then filter
 
        results = []
        for score, idx in zip(sims[0], idxs[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
 
            # Apply filters if given (e.g., {"document_id": "abc"})
            if filters:
                match = all(meta.get(k) == v for k, v in filters.items())
                if not match:
                    continue
 
            results.append({**meta, "score": float(score)})
 
            if len(results) >= top_k:
                break
        return results
 
    def rebuild(self, embeddings: np.ndarray, metadatas: List[Dict[str, Any]]):
        """Rebuild the FAISS index from scratch."""
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
 
        embeddings = self._normalize(embeddings).astype("float32")
 
        if isinstance(self.index, faiss.IndexIVFFlat):
            self.index = faiss.IndexIVFFlat(
                faiss.IndexFlatIP(self.dim),
                self.dim,
                self.index.nlist,
                faiss.METRIC_INNER_PRODUCT
            )
            self.index.train(embeddings)
        else:
            self.index = faiss.IndexFlatIP(self.dim)
 
        self.index.add(embeddings)
        self.metadata = metadatas
        self.save()
 
 
# ✅ Singleton instance
# Use Flat for small scale, IVF for big data
faiss_index = FaissIndex(dim=384, use_ivf=False, nlist=200)