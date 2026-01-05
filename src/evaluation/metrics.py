from typing import List, Dict
from anthropic import Anthropic
import os
import re

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
            score = float(re.search(r'\d+', score_text).group())
            return min(max(score, 0), 5)
        except:
            return 0.0
    
    def faithfulness(self, answer: str, context_chunks: List[str]) -> float:
        """Check if answer is grounded in context"""
        context = "\n\n".join(context_chunks)
        
        prompt = f"""Does the answer contain ANY information NOT in the context?

Context: {context}

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
    
    def evaluate_response(
        self,
        question: str,
        answer: str,
        retrieved_chunks: List[str]
    ) -> Dict:
        """Run all evaluation metrics"""
        print(f"  Evaluating: {question[:40]}...")
        
        metrics = {
            'answer_relevancy': self.answer_relevancy(question, answer),
            'faithfulness': self.faithfulness(answer, retrieved_chunks)
        }
        
        # Overall score (weighted average)
        metrics['overall_score'] = (
            metrics['answer_relevancy'] / 5 * 0.5 +
            metrics['faithfulness'] * 0.5
        )
        
        return metrics