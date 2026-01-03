import os
from typing import List, Dict, Tuple
from anthropic import Anthropic

class AnswerGenerator:
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("❌ ANTHROPIC_API_KEY not found in .env file")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = """You are a helpful AI assistant that answers questions based on provided context.

Rules:
1. Only use information from the provided context
2. If the answer is not in the context, say "I don't have enough information"
3. Cite sources using [1], [2], etc.
4. Be concise but complete
5. Do not make up information"""
    
    def _format_context(self, chunks: List[Tuple[Dict, float]]) -> str:
        context_parts = []
        for i, (chunk, score) in enumerate(chunks, 1):
            context_parts.append(f"[{i}] {chunk['content']}\n")
        return "\n".join(context_parts)
    
    def generate(
        self, 
        question: str, 
        retrieved_chunks: List[Tuple[Dict, float]],
        max_tokens: int = 500
    ) -> Dict:
        context = self._format_context(retrieved_chunks)
        
        user_prompt = f"""Context:
{context}

Question: {question}

Answer using ONLY the context above. Include citations [1], [2], etc."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            answer = response.content[0].text
            
            sources = [
                {
                    'chunk_id': chunk['chunk_id'],
                    'doc_title': chunk['doc_title'],
                    'content': chunk['content'][:200] + '...',
                    'score': score
                }
                for chunk, score in retrieved_chunks
            ]
            
            return {
                'question': question,
                'answer': answer,
                'sources': sources,
                'model': self.model,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens
            }
        
        except Exception as e:
            return {
                'question': question,
                'answer': f"Error: {str(e)}",
                'sources': [],
                'model': self.model,
                'tokens_used': 0
            }