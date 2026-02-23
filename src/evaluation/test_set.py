from typing import List, Dict
import json
from pathlib import Path

class TestSetGenerator:
    """Generate and manage test questions"""
    
    def __init__(self):
        self.test_questions = self._create_test_set()
    
   
    def _create_test_set(self) -> List[Dict]:
        """Create a comprehensive test set"""
        return [
            {
                'question': 'What is machine learning?',
                'category': 'definition',
                'difficulty': 'easy'
            },
            {
                'question': 'How do neural networks learn from data?',
                'category': 'technical',
                'difficulty': 'medium'
            },
            {
                'question': 'What are the main types of machine learning?',
                'category': 'classification',
                'difficulty': 'easy'
            },
            {
                'question': 'Explain backpropagation in neural networks',
                'category': 'technical',
                'difficulty': 'hard'
            },
            {
                'question': 'What is the difference between supervised and unsupervised learning?',
                'category': 'comparison',
                'difficulty': 'medium'
            },
            {
                'question': 'How do convolutional neural networks process images?',
                'category': 'technical',
                'difficulty': 'hard'
            },
            {
                'question': 'What is transfer learning?',
                'category': 'definition',
                'difficulty': 'medium'
            },
            {
                'question': 'What are transformer architectures used for?',
                'category': 'application',
                'difficulty': 'medium'
            },
            {
                'question': 'How does gradient descent optimize model parameters?',
                'category': 'technical',
                'difficulty': 'hard'
            },
            {
                'question': 'What is overfitting and how can it be prevented?',
                'category': 'problem-solving',
                'difficulty': 'medium'
            },
            {
                'question': 'Explain the role of activation functions',
                'category': 'technical',
                'difficulty': 'medium'
            },
            {
                'question': 'What is reinforcement learning?',
                'category': 'definition',
                'difficulty': 'easy'
            },
            {
                'question': 'How do attention mechanisms work?',
                'category': 'technical',
                'difficulty': 'hard'
            },
            {
                'question': 'What are the challenges in training deep networks?',
                'category': 'problem-solving',
                'difficulty': 'hard'
            },
            {
                'question': 'What is the purpose of regularization?',
                'category': 'technical',
                'difficulty': 'medium'
            }
        ]
    
    def get_test_set(self) -> List[Dict]:
        """Get the full test set"""
        return self.test_questions
    
    def get_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get questions by difficulty"""
        return [q for q in self.test_questions if q['difficulty'] == difficulty]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get questions by category"""
        return [q for q in self.test_questions if q['category'] == category]
    
    def save(self, filepath: str):
        """Save test set to file"""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.test_questions, f, indent=2)
        
        print(f"✅ Saved {len(self.test_questions)} test questions to {filepath}")
