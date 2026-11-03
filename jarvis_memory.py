import os
import numpy as np
import json
import faiss
from sentence_transformers import SentenceTransformer

class JarvisMemoryCoordinator:
    def __init__(self, db_dir="/content/memory_db", embedding_model_name="all-MiniLM-L6-v2"):
        self.db_dir = db_dir
        self.index_path = os.path.join(db_dir, "faiss_index.bin")
        self.meta_path = os.path.join(db_dir, "metadata.json")
        self.short_term_buffer = []
        self.dimension = 384
        os.makedirs(db_dir, exist_ok=True)
        self.model = SentenceTransformer(embedding_model_name, device="cpu")
        self._init_vector_db()

    def _init_vector_db(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception:
                self._create_empty_index()
        else:
            self._create_empty_index()

    def _create_empty_index(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        self.save_index()

    def save_index(self) :
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_short_term_memory(self, user_input, response):
        self.short_term_buffer.append({"user": user_input, "bot": response})
        if len(self.short_term_buffer) > 10:
            self.short_term_buffer.pop(0)

    def commit_to_long_term_memory(self, text, info_dict=None):
        if not text.strip(): return
        embedding = self.model.encode([text])[0].astype("float32")
        self.index.add(np.expand_dims(embedding, axis=0))
        self.metadata.append({"text": text, "details": info_dict or {}})
        self.save_index()

    def search_memories(self, query, top_k=3):
        if self.index.ntotal == 0: return []
        query_vector = self.model.encode([query])[0].astype("float32")
        distances, indices = self.index.search(np.expand_dims(query_vector, axis=0), min(top_k, self.index.ntotal))
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append({"memory": self.metadata[idx], "distance": float(distances[0][i])})
        return results

    def get_short_term_context(self):
        return self.short_term_buffer
