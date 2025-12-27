from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Tuple
import pickle
from pathlib import Path

class VectorSearch:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        print(f"📥 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.chunks = None
        print(f"✅ Model loaded (dimension: {self.dimension})")
    
    def create_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        texts = [chunk['content'] for chunk in chunks]
        
        print(f"🔢 Generating embeddings for {len(texts)} chunks...")
        print("⏰ This takes ~10-15 minutes on CPU...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        return embeddings.astype('float32')
    
    def build_index(self, chunks: List[Dict]):
        self.chunks = chunks
        embeddings = self.create_embeddings(chunks)
        
        print(f"🏗️ Building FAISS index...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
        
        print(f"✅ Index built with {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        query_embedding = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            similarity = 1 / (1 + dist)
            results.append((self.chunks[idx], similarity))
        
        return results
    
    def save(self, path: str):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(self.index, str(save_path / 'faiss.index'))
        
        with open(save_path / 'chunks.pkl', 'wb') as f:
            pickle.dump(self.chunks, f)
        
        print(f"✅ Saved vector index to {path}")
    
    def load(self, path: str):
        load_path = Path(path)
        self.index = faiss.read_index(str(load_path / 'faiss.index'))
        
        with open(load_path / 'chunks.pkl', 'rb') as f:
            self.chunks = pickle.load(f)
        
        print(f"✅ Loaded index with {self.index.ntotal} vectors")