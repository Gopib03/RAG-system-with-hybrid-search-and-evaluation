from pathlib import Path
import json
import sys
sys.path.append('src')

from ingestion.loader import DocumentLoader
from ingestion.chunker import DocumentChunker

print("🚀 Starting document ingestion...")

print("\n📂 Loading documents...")
loader = DocumentLoader('data/raw/arxiv')
documents = loader.load_all()
print(f"✅ Loaded {len(documents)} documents")

print("\n✂️ Chunking documents...")
chunker = DocumentChunker(chunk_size=1024, chunk_overlap=128)
chunks = chunker.chunk_documents(documents)
print(f"✅ Created {len(chunks)} chunks")

output_path = Path('data/processed/chunks.json')
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(chunks, f, indent=2)

print(f"\n💾 Saved to {output_path}")

total_chars = sum(c['metadata']['char_count'] for c in chunks)
total_words = sum(c['metadata']['word_count'] for c in chunks)

print("\n📊 Statistics:")
print(f"  Documents: {len(documents)}")
print(f"  Chunks: {len(chunks)}")
print(f"  Avg chunks/doc: {len(chunks)/len(documents):.1f}")
print(f"  Total words: {total_words:,}")
print(f"  Avg words/chunk: {total_words/len(chunks):.0f}")
print("\n✅ Ingestion complete!")