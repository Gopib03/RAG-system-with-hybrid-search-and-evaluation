from rank_bm25 import BM25Okapi
from typing import List, Dict, Tuple
import pickle
from pathlib import Path

class KeywordSearch:
    def __init__(self):
        self.bm25 = None
        self.chunks = None
    
    def build_index(self, chunks: List[Dict]):
        self.chunks = chunks
        
        print(f"🏗️ Building BM25 keyword index...")
        tokenized_docs = [chunk['content'].lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_docs)
        
        print(f"✅ BM25 index built with {len(chunks)} documents")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        top_k_indices = scores.argsort()[-k:][::-1]
        
        results = []
        for idx in top_k_indices:
            results.append((self.chunks[idx], float(scores[idx])))
        
        return results
    
    def save(self, path: str):
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        with open(save_path / 'bm25.pkl', 'wb') as f:
            pickle.dump({'bm25': self.bm25, 'chunks': self.chunks}, f)
        
        print(f"✅ Saved keyword index to {path}")
    
    def load(self, path: str):
        load_path = Path(path)
        
        with open(load_path / 'bm25.pkl', 'rb') as f:
            data = pickle.load(f)
            self.bm25 = data['bm25']
            self.chunks = data['chunks']
        
        print(f"✅ Loaded keyword index with {len(self.chunks)} documents")