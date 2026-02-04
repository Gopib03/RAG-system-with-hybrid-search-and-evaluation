from typing import List, Dict
from anthropic import Anthropic
import os
import re
import time

class RAGEvaluator:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        self.client = Anthropic(api_key=api_key)
    
    def answer_relevancy(self, question: str, answer: str) -> float:
        """Rate answer relevancy 0-5"""
        prompt = f"""Rate this answer's relevancy on a scale of 0-5.

Question: {question}
Answer: {answer}

Provide ONLY a number 0-5."""
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            
            score_text = response.content[0].text.strip()
            score = float(re.search(r'\d+\.?\d*', score_text).group())
            return min(max(score, 0), 5)
        except:
            return 0.0
    
    def faithfulness(self, answer: str, context_chunks: List[str]) -> float:
        """Check if answer is grounded in context (0-1)"""
        context = "\n\n".join(context_chunks[:3])  # Use top 3 chunks
        
        prompt = f"""Does the answer contain information NOT in the context?

Context: {context[:2000]}

Answer: {answer}

Reply ONLY 'yes' or 'no'."""
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text.strip().lower()
            return 0.0 if 'yes' in result else 1.0
        except:
            return 0.0
    
    def context_precision(self, question: str, context_chunks: List[str]) -> float:
        """What % of retrieved chunks are relevant? (0-1)"""
        if not context_chunks:
            return 0.0
        
        relevant_count = 0
        
        for chunk in context_chunks:
            prompt = f"""Is this context relevant for answering the question?

Question: {question}
Context: {chunk[:500]}

Reply ONLY 'yes' or 'no'."""
            
            try:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = response.content[0].text.strip().lower()
                if 'yes' in result:
                    relevant_count += 1
            except:
                continue
        
        return relevant_count / len(context_chunks)
    
    def evaluate_response(
        self,
        question: str,
        answer: str,
        retrieved_chunks: List[str],
        measure_latency: bool = False
    ) -> Dict:
        """Run all evaluation metrics"""
        
        start_time = time.time() if measure_latency else None
        
        print(f"  Evaluating: {question[:50]}...")
        
        metrics = {
            'answer_relevancy': self.answer_relevancy(question, answer),
            'faithfulness': self.faithfulness(answer, retrieved_chunks),
            'context_precision': self.context_precision(question, retrieved_chunks[:5])
        }
        
        # Overall score (weighted average)
        metrics['overall_score'] = (
            metrics['answer_relevancy'] / 5 * 0.4 +
            metrics['faithfulness'] * 0.3 +
            metrics['context_precision'] * 0.3
        )
        
        if measure_latency:
            metrics['evaluation_time_s'] = time.time() - start_time
        
        return metrics