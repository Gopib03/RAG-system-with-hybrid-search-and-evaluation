from typing import List, Dict, Tuple
from .vector_search import VectorSearch
from .keyword_search import KeywordSearch

class HybridSearch:
    def __init__(self, vector_weight: float = 0.7, keyword_weight: float = 0.3):
        self.vector_search = VectorSearch()
        self.keyword_search = KeywordSearch()
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
    
    def build_index(self, chunks: List[Dict]):
        print("\n🔧 Building hybrid search index...")
        print("="*60)
        self.vector_search.build_index(chunks)
        self.keyword_search.build_index(chunks)
        print("="*60)
        print("✅ Hybrid index complete!")
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        vector_results = self.vector_search.search(query, k=k*2)
        keyword_results = self.keyword_search.search(query, k=k*2)
        
        vector_scores = self._normalize([s for _, s in vector_results])
        keyword_scores = self._normalize([s for _, s in keyword_results])
        
        combined = {}
        
        for (chunk, _), norm_score in zip(vector_results, vector_scores):
            cid = chunk['chunk_id']
            combined[cid] = {
                'chunk': chunk,
                'score': self.vector_weight * norm_score
            }
        
        for (chunk, _), norm_score in zip(keyword_results, keyword_scores):
            cid = chunk['chunk_id']
            if cid in combined:
                combined[cid]['score'] += self.keyword_weight * norm_score
            else:
                combined[cid] = {
                    'chunk': chunk,
                    'score': self.keyword_weight * norm_score
                }
        
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:k]
        
        return [(item['chunk'], item['score']) for item in sorted_results]
    
    def _normalize(self, scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]
    
    def save(self, path: str):
        self.vector_search.save(path)
        self.keyword_search.save(path)
        print(f"💾 Saved complete hybrid index to {path}")
    
    def load(self, path: str):
        self.vector_search.load(path)
        self.keyword_search.load(path)
        print(f"✅ Loaded complete hybrid index from {path}")