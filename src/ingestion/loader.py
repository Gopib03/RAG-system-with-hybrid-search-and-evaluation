from pathlib import Path
from typing import List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
    
    def load_json(self, filepath: Path) -> Dict:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all(self) -> List[Dict]:
        documents = []
        
        for filepath in self.data_dir.rglob('*.json'):
            try:
                doc = self.load_json(filepath)
                documents.append(doc)
                
                if len(documents) % 50 == 0:
                    logger.info(f"Loaded {len(documents)} documents...")
            
            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")
        
        logger.info(f"✅ Loaded {len(documents)} documents total")
        return documents

if __name__ == '__main__':
    loader = DocumentLoader('data/raw/arxiv')
    docs = loader.load_all()
    print(f"\n📊 Sample document:")
    print(f"Title: {docs[0]['title']}")
    print(f"Length: {len(docs[0]['content'])} chars")