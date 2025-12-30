import json
import sys
from pathlib import Path
sys.path.append('src')

from retrieval.hybrid import HybridSearch

print("\n" + "="*60)
print("🚀 BUILDING SEARCH INDICES")
print("="*60)

print("\n📂 Loading chunks from disk...")
with open('data/processed/chunks.json') as f:
    chunks = json.load(f)
print(f"✅ Loaded {len(chunks)} chunks")

print(f"\n⏰ Starting index build...")
print("   This takes ~10-15 minutes on CPU")
print("   Perfect time for a coffee break! ☕")
print()

hybrid = HybridSearch(vector_weight=0.7, keyword_weight=0.3)
hybrid.build_index(chunks)

print("\n💾 Saving indices to disk...")
hybrid.save('data/embeddings/hybrid_index')

print("\n🔍 Testing search with sample query...")
print("-"*60)
results = hybrid.search("machine learning models", k=3)

for i, (chunk, score) in enumerate(results, 1):
    print(f"\n{i}. Score: {score:.3f}")
    print(f"   Doc: {chunk['doc_title'][:50]}...")
    print(f"   Text: {chunk['content'][:100]}...")

print("\n" + "="*60)
print("✅ ALL INDICES BUILT SUCCESSFULLY!")
print("="*60)
print("\n📊 Summary:")
print(f"   Total chunks indexed: {len(chunks)}")
print(f"   Vector dimensions: 384")
print(f"   Storage location: data/embeddings/hybrid_index/")
print()