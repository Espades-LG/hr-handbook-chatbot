"""
Search module for semantic retrieval
Uses embeddings to find relevant handbook content
"""

import logging
import numpy as np
from typing import List, Tuple, Dict

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from src.config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    SIMILARITY_THRESHOLD,
    MAX_RESULTS,
)

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Semantic search using embeddings"""
    
    def __init__(self, documents: Dict[str, str]):
        """
        Initialize semantic search
        
        Args:
            documents: Dictionary of {filename: content}
        """
        self.documents = documents
        self.embeddings = {}
        self.chunks = []
        
        if OpenAI and OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self._chunk_and_embed()
        else:
            logger.warning("OpenAI API not configured; using keyword search fallback")
            self.client = None
    
    def _chunk_and_embed(self):
        """
        Split documents into chunks and create embeddings
        """
        try:
            for filename, content in self.documents.items():
                chunks = self._split_text(content, chunk_size=500, overlap=50)
                
                for i, chunk in enumerate(chunks):
                    # Create embedding
                    response = self.client.embeddings.create(
                        input=chunk,
                        model=EMBEDDING_MODEL
                    )
                    embedding = response.data[0].embedding
                    
                    self.chunks.append({
                        "id": f"{filename}_{i}",
                        "filename": filename,
                        "text": chunk,
                        "embedding": embedding
                    })
            
            logger.info(f"Created {len(self.chunks)} embeddings")
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            self.client = None
    
    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        sentences = text.split('. ')
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            if current_size + len(sentence) > chunk_size and current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
                # Keep last few sentences for overlap
                current_chunk = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_size = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_size += len(sentence)
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def search(self, query: str, top_k: int = MAX_RESULTS) -> List[Dict]:
        """
        Search for relevant content using embeddings
        
        Args:
            query: User question/query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with scores
        """
        if not self.client or not self.chunks:
            logger.warning("Using keyword search fallback")
            return self._keyword_search(query, top_k)
        
        try:
            # Get embedding for query
            response = self.client.embeddings.create(
                input=query,
                model=EMBEDDING_MODEL
            )
            query_embedding = response.data[0].embedding
            
            # Calculate similarity scores
            scores = []
            for chunk in self.chunks:
                similarity = self._cosine_similarity(
                    query_embedding,
                    chunk["embedding"]
                )
                
                if similarity >= SIMILARITY_THRESHOLD:
                    scores.append({
                        "id": chunk["id"],
                        "filename": chunk["filename"],
                        "text": chunk["text"],
                        "score": similarity
                    })
            
            # Sort by score and return top k
            scores.sort(key=lambda x: x["score"], reverse=True)
            return scores[:top_k]
        
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self._keyword_search(query, top_k)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """
        Fallback keyword search when embeddings not available
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Matching results
        """
        query_words = query.lower().split()
        results = []
        
        for chunk in self.chunks:
            text_lower = chunk["text"].lower()
            matches = sum(1 for word in query_words if word in text_lower)
            score = matches / len(query_words) if query_words else 0
            
            if score > 0:
                results.append({
                    "id": chunk["id"],
                    "filename": chunk["filename"],
                    "text": chunk["text"],
                    "score": score
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
