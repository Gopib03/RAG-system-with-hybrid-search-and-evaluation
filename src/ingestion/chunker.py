from typing import List, Dict
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentChunker:
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """Simple sliding window chunking"""
        text = self.clean_text(text)
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            if chunk:
                chunks.append(chunk)
            
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        content = document.get('content', '')
        text_chunks = self.chunk_text(content)
        
        chunk_docs = []
        for idx, chunk_text in enumerate(text_chunks):
            chunk_doc = {
                'chunk_id': f"{document['id']}_chunk_{idx}",
                'doc_id': document['id'],
                'doc_title': document.get('title', ''),
                'chunk_index': idx,
                'content': chunk_text,
                'metadata': {
                    'total_chunks': len(text_chunks),
                    'char_count': len(chunk_text),
                    'word_count': len(chunk_text.split())
                }
            }
            chunk_docs.append(chunk_doc)
        
        return chunk_docs
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(f"✅ Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

if __name__ == '__main__':
    from loader import DocumentLoader
    import json
    
    loader = DocumentLoader('data/raw/arxiv')
    docs = loader.load_all()
    
    chunker = DocumentChunker(chunk_size=1024, chunk_overlap=128)
    chunks = chunker.chunk_documents(docs)
    
    output_path = Path('data/processed/chunks.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"✅ Saved {len(chunks)} chunks to {output_path}")