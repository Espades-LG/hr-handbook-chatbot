"""
Chatbot handler for HR Handbook
Main logic for processing questions and generating responses
"""

import logging
from typing import List, Dict, Tuple

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from src.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    DEFAULT_RESPONSE,
    ESCALATION_TOPICS,
)
from src.retrieval.search import SemanticSearch

logger = logging.getLogger(__name__)


class HRChatbot:
    """Main HR Handbook Chatbot"""
    
    def __init__(self, search_engine: SemanticSearch):
        """
        Initialize the chatbot
        
        Args:
            search_engine: SemanticSearch instance for retrieval
        """
        self.search_engine = search_engine
        self.conversation_history = []
        
        if OpenAI and OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            logger.warning("OpenAI API not configured")
            self.client = None
    
    def process_question(self, question: str) -> Dict:
        """
        Process a user question and generate response
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        logger.info(f"Processing question: {question}")
        
        # Check for escalation topics
        if self._should_escalate(question):
            return self._escalation_response(question)
        
        # Search handbook
        search_results = self.search_engine.search(question, top_k=3)
        
        if not search_results:
            logger.warning("No search results found")
            return self._no_match_response(question)
        
        # Generate response using LLM
        if self.client:
            response = self._generate_llm_response(question, search_results)
        else:
            response = self._generate_fallback_response(question, search_results)
        
        return {
            "answer": response["answer"],
            "sources": response["sources"],
            "confidence": response["confidence"],
            "escalation": False
        }
    
    def _should_escalate(self, question: str) -> bool:
        """
        Check if question should be escalated to HR
        
        Args:
            question: User's question
            
        Returns:
            True if escalation needed
        """
        question_lower = question.lower()
        
        for topic in ESCALATION_TOPICS:
            if topic in question_lower:
                return True
        
        return False
    
    def _escalation_response(self, question: str) -> Dict:
        """
        Generate escalation response for sensitive topics
        
        Args:
            question: User's question
            
        Returns:
            Escalation response
        """
        return {
            "answer": """I understand you have a sensitive question. 
This topic is best discussed directly with our HR team who can provide 
personalized guidance.

**Contact HR:**
- Email: hr@company.com
- Phone: [PHONE]
- Office hours: [HOURS]

They'll be happy to help you within [TIMEFRAME - e.g., 1 business day].""",
            "sources": [],
            "confidence": 1.0,
            "escalation": True
        }
    
    def _generate_llm_response(
        self,
        question: str,
        search_results: List[Dict]
    ) -> Dict:
        """
        Generate response using LLM
        
        Args:
            question: User's question
            search_results: Search results from handbook
            
        Returns:
            Response with answer and sources
        """
        # Prepare context from search results
        context = "\n\n".join([
            f"Source: {r['filename']}\n{r['text']}"
            for r in search_results
        ])
        
        # Create system prompt
        system_prompt = """You are a helpful HR assistant for a company. 
You answer questions based on the company's HR handbook.

IMPORTANT RULES:
1. Answer ONLY based on the provided handbook content
2. If the handbook doesn't cover something, say "I don't have that information"
3. Always cite the handbook section where you found the answer
4. Be professional, empathetic, and clear
5. Use bullet points and formatting for readability
6. Keep responses concise (under 1000 words)
7. If the question is about personal/confidential matters, recommend HR contact

HANDBOOK CONTENT:
{context}"""
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt.format(context=context)
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            answer = response.choices[0].message.content
            
            # Extract source files
            sources = list(set([r["filename"] for r in search_results]))
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.9  # High confidence for LLM responses
            }
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_fallback_response(question, search_results)
    
    def _generate_fallback_response(
        self,
        question: str,
        search_results: List[Dict]
    ) -> Dict:
        """
        Generate simple response without LLM
        
        Args:
            question: User's question
            search_results: Search results
            
        Returns:
            Simple formatted response
        """
        # Combine relevant excerpts
        answer = "Based on the handbook:\n\n"
        
        for result in search_results:
            answer += f"• {result['text'][:200]}...\n\n"
        
        answer += "\nFor more details or clarification, contact HR at hr@company.com"
        
        return {
            "answer": answer,
            "sources": [r["filename"] for r in search_results],
            "confidence": 0.7
        }
    
    def _no_match_response(self, question: str) -> Dict:
        """
        Generate response when no matches found
        
        Args:
            question: User's question
            
        Returns:
            No match response
        """
        return {
            "answer": DEFAULT_RESPONSE,
            "sources": [],
            "confidence": 0.0,
            "escalation": True
        }
    
    def add_to_history(self, role: str, content: str):
        """
        Add message to conversation history
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
