"""
Generation Service
Handles LLM generation using Anthropic Claude API
"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)


class ClaudeGenerator:
    """Generate responses using Claude API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize Claude generator
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or parameters")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        logger.info(f"Initialized Claude generator with model: {model}")
    
    def generate_answer(
        self,
        query: str,
        context: str,
        subject: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """
        Generate an answer using RAG context
        
        Args:
            query: User's question
            context: Retrieved context from vector store
            subject: Subject area (math/physics)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            system_prompt: Custom system prompt (optional)
            
        Returns:
            Dict with 'answer', 'usage', and metadata
        """
        # Default system prompt for tutoring
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt(subject)
        
        # Construct the user message with context
        user_message = self._construct_rag_prompt(query, context, subject)
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract response
            answer = response.content[0].text
            
            # Get usage info
            usage = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
            
            logger.info(f"Generated answer. Tokens used: {usage['total_tokens']}")
            
            return {
                'answer': answer,
                'usage': usage,
                'model': self.model,
                'subject': subject
            }
        
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def _get_default_system_prompt(self, subject: str) -> str:
        """Get default system prompt for tutoring"""
        return f"""You are an expert {subject} tutor. Your role is to help students understand {subject} concepts clearly and thoroughly.

Guidelines:
1. Base your answers ONLY on the provided context documents
2. If the context doesn't contain enough information to answer fully, say so explicitly
3. Explain concepts step-by-step in a clear, educational manner
4. Use examples when helpful
5. If you notice the student might be confused about prerequisites, gently point this out
6. Be encouraging and supportive
7. If asked about topics outside of {subject}, politely redirect to {subject} topics
8. Never make up information - only use what's in the context

When answering:
- Start with a direct answer to the question
- Provide explanation and reasoning
- Include relevant formulas, definitions, or principles from the context
- End with a brief summary or key takeaway if appropriate
"""
    
    def _construct_rag_prompt(self, query: str, context: str, subject: str) -> str:
        """Construct the RAG prompt combining query and context"""
        if not context or context.strip() == '':
            return f"""Question about {subject}:
{query}

Note: No relevant context documents were found. Please explain that you need specific {subject} materials to provide an accurate answer, and ask the student to rephrase their question or verify that the course materials have been uploaded."""
        
        prompt = f"""Using the following context from {subject} course materials, please answer the student's question.

Context Documents:
{context}

Student's Question:
{query}

Please provide a clear, educational answer based on the context above."""
        
        return prompt
    
    def generate_streaming_answer(
        self,
        query: str,
        context: str,
        subject: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """
        Generate answer with streaming (for real-time responses)
        
        Args:
            Same as generate_answer
            
        Yields:
            Text chunks as they are generated
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt(subject)
        
        user_message = self._construct_rag_prompt(query, context, subject)
        
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            raise
    
    def generate_follow_up_questions(
        self,
        query: str,
        answer: str,
        subject: str,
        num_questions: int = 3
    ) -> List[str]:
        """
        Generate follow-up questions to deepen understanding
        
        Args:
            query: Original query
            answer: Generated answer
            subject: Subject area
            num_questions: Number of follow-up questions
            
        Returns:
            List of follow-up questions
        """
        prompt = f"""Based on this {subject} question and answer, generate {num_questions} thoughtful follow-up questions that would help the student deepen their understanding.

Original Question: {query}

Answer Given: {answer}

Generate {num_questions} follow-up questions that:
1. Build on the concepts discussed
2. Explore related topics
3. Test deeper understanding
4. Are appropriate for a student learning {subject}

Format: Return only the questions, one per line, numbered 1-{num_questions}."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                temperature=0.8,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse questions
            questions_text = response.content[0].text
            questions = [
                q.strip() 
                for q in questions_text.split('\n') 
                if q.strip() and any(char.isdigit() for char in q[:3])
            ]
            
            # Remove numbering
            questions = [q.split('.', 1)[1].strip() if '.' in q else q for q in questions]
            
            return questions[:num_questions]
        
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            return []


# Singleton instance
_generator = None

def get_claude_generator(api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514") -> ClaudeGenerator:
    """
    Get or create Claude generator singleton
    
    Args:
        api_key: Anthropic API key
        model: Model to use
        
    Returns:
        ClaudeGenerator instance
    """
    global _generator
    
    if _generator is None:
        _generator = ClaudeGenerator(api_key, model)
    
    return _generator
