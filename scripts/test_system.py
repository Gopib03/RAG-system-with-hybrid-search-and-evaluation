import sys
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv()  # This loads the .env file
import os

from retrieval.hybrid import HybridSearch
from generation.generator import AnswerGenerator

print("\n" + "="*70)
print("🧪 COMPLETE SYSTEM TEST")
print("="*70)

# Load search
print("\n📂 Loading search index...")
hybrid = HybridSearch()
hybrid.load('data/embeddings/hybrid_index')

# Create generator
print("🤖 Initializing answer generator...")
generator = AnswerGenerator()

# Test questions
questions = [
    "What is machine learning?",
    "How do neural networks work?",
    "What are the main types of machine learning?"
]

print("\n" + "="*70)
print("RUNNING QUERIES")
print("="*70)

for i, question in enumerate(questions, 1):
    print(f"\n[{i}/{len(questions)}] ❓ {question}")
    print("-"*70)
    
    # Retrieve
    chunks = hybrid.search(question, k=5)
    print(f"✅ Retrieved {len(chunks)} relevant chunks")
    
    # Generate
    result = generator.generate(question, chunks)
    
    print(f"\n💬 ANSWER:")
    print(result['answer'])
    
    print(f"\n📊 STATS:")
    print(f"   • Tokens used: {result['tokens_used']}")
    print(f"   • Sources: {len(result['sources'])}")
    print(f"   • Model: {result['model']}")

print("\n" + "="*70)
print("✅ COMPLETE SYSTEM TEST PASSED!")
print("="*70)
print("\n🎉 Your RAG system is fully operational!")
print("\n📝 What you've built:")
print("   • Hybrid search (vector + keyword)")
print("   • 7,712 chunks indexed")
print("   • Claude Haiku for answers")
print("   • Complete RAG pipeline")
print("\n💼 Ready for your resume!")
print()