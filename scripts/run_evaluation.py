import sys
sys.path.append('src')

from retrieval.hybrid import HybridSearch
from generation.generator import AnswerGenerator
from evaluation.metrics import RAGEvaluator
from evaluation.test_set import TestSetGenerator

import json
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*70)
print("📊 COMPREHENSIVE RAG EVALUATION")
print("="*70)

# Load components
print("\n📂 Loading system components...")
search = HybridSearch()
search.load('data/embeddings/hybrid_index')

generator = AnswerGenerator()
evaluator = RAGEvaluator()

# Get test set
print("📝 Loading test questions...")
test_gen = TestSetGenerator()
test_questions = test_gen.get_test_set()
print(f"✅ Loaded {len(test_questions)} test questions")

# Run evaluation
results = []
total_start = time.time()

print("\n" + "="*70)
print("RUNNING EVALUATION")
print("="*70)

for i, test_item in enumerate(test_questions, 1):
    question = test_item['question']
    
    print(f"\n[{i}/{len(test_questions)}] {question}")
    print("-"*70)
    
    # Retrieve
    retrieval_start = time.time()
    chunks = search.search(question, k=5)
    retrieval_time = time.time() - retrieval_start
    
    # Generate
    generation_start = time.time()
    response = generator.generate(question, chunks)
    generation_time = time.time() - generation_start
    
    # Evaluate
    context_texts = [c['content'] for c, _ in chunks]
    metrics = evaluator.evaluate_response(
        question,
        response['answer'],
        context_texts
    )
    
    # Store result
    result = {
        'question': question,
        'category': test_item['category'],
        'difficulty': test_item['difficulty'],
        'answer': response['answer'],
        'metrics': metrics,
        'performance': {
            'retrieval_time_ms': retrieval_time * 1000,
            'generation_time_ms': generation_time * 1000,
            'total_time_ms': (retrieval_time + generation_time) * 1000,
            'tokens_used': response['tokens_used']
        }
    }
    
    results.append(result)
    
    # Print metrics
    print(f"  ✅ Relevancy: {metrics['answer_relevancy']:.2f}/5")
    print(f"  ✅ Faithfulness: {metrics['faithfulness']:.0%}")
    print(f"  ✅ Precision: {metrics['context_precision']:.0%}")
    print(f"  ✅ Overall: {metrics['overall_score']:.0%}")
    print(f"  ⏱ Time: {result['performance']['total_time_ms']:.0f}ms")
    print(f"  🔢 Tokens: {result['performance']['tokens_used']}")

total_time = time.time() - total_start

# Calculate aggregate metrics
print("\n" + "="*70)
print("AGGREGATE RESULTS")
print("="*70)

aggregate = {
    'total_questions': len(results),
    'avg_relevancy': sum(r['metrics']['answer_relevancy'] for r in results) / len(results),
    'avg_faithfulness': sum(r['metrics']['faithfulness'] for r in results) / len(results),
    'avg_precision': sum(r['metrics']['context_precision'] for r in results) / len(results),
    'avg_overall_score': sum(r['metrics']['overall_score'] for r in results) / len(results),
    'avg_latency_ms': sum(r['performance']['total_time_ms'] for r in results) / len(results),
    'p95_latency_ms': sorted([r['performance']['total_time_ms'] for r in results])[int(len(results) * 0.95)],
    'p99_latency_ms': sorted([r['performance']['total_time_ms'] for r in results])[int(len(results) * 0.99)],
    'total_tokens': sum(r['performance']['tokens_used'] for r in results),
    'avg_tokens_per_query': sum(r['performance']['tokens_used'] for r in results) / len(results),
    'total_evaluation_time_s': total_time
}

print(f"\n📊 Quality Metrics:")
print(f"  Answer Relevancy:    {aggregate['avg_relevancy']:.2f}/5.0")
print(f"  Faithfulness:        {aggregate['avg_faithfulness']:.1%}")
print(f"  Context Precision:   {aggregate['avg_precision']:.1%}")
print(f"  Overall Score:       {aggregate['avg_overall_score']:.1%}")

print(f"\n⚡ Performance Metrics:")
print(f"  Avg Latency:         {aggregate['avg_latency_ms']:.0f}ms")
print(f"  P95 Latency:         {aggregate['p95_latency_ms']:.0f}ms")
print(f"  P99 Latency:         {aggregate['p99_latency_ms']:.0f}ms")

print(f"\n💰 Cost Metrics:")
print(f"  Total Tokens:        {aggregate['total_tokens']:,}")
print(f"  Avg Tokens/Query:    {aggregate['avg_tokens_per_query']:.0f}")
print(f"  Est. Cost:           ${aggregate['total_tokens'] * 0.00000025:.4f}")

print(f"\n⏱ Evaluation Time:    {aggregate['total_evaluation_time_s']:.1f}s")

# Save results
output_dir = Path('data/evaluation')
output_dir.mkdir(parents=True, exist_ok=True)

output = {
    'aggregate_metrics': aggregate,
    'individual_results': results
}

output_path = output_dir / 'evaluation_results.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n💾 Results saved to: {output_path}")

print("\n" + "="*70)
print("✅ EVALUATION COMPLETE!")
print("="*70)