"""
Loader module for HR Handbook
Reads markdown files and prepares them for search
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class HandbookLoader:
    """Loads and parses handbook markdown files"""
    
    def __init__(self, handbook_dir: str):
        """
        Initialize the handbook loader
        
        Args:
            handbook_dir: Directory containing markdown files
        """
        self.handbook_dir = handbook_dir
        self.documents = {}
        self.sections = {}
    
    def load_handbook(self) -> Dict[str, str]:
        """
        Load all handbook markdown files
        
        Returns:
            Dictionary mapping filename to content
        """
        handbook_content = {}
        
        if not os.path.exists(self.handbook_dir):
            logger.warning(f"Handbook directory not found: {self.handbook_dir}")
            return handbook_content
        
        for filename in os.listdir(self.handbook_dir):
            if filename.endswith(".md"):
                filepath = os.path.join(self.handbook_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        handbook_content[filename] = content
                        logger.info(f"Loaded: {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
        
        self.documents = handbook_content
        return handbook_content
    
    def parse_sections(self) -> Dict[str, List[Dict]]:
        """
        Parse handbook into sections based on markdown headers
        
        Returns:
            Dictionary mapping section to list of content blocks
        """
        sections = {}
        
        for filename, content in self.documents.items():
            sections[filename] = self._parse_markdown(content)
        
        self.sections = sections
        return sections
    
    def _parse_markdown(self, content: str) -> List[Dict]:
        """
        Parse markdown content into sections
        
        Args:
            content: Raw markdown content
            
        Returns:
            List of sections with headers and text
        """
        lines = content.split('\n')
        sections = []
        current_section = {
            "title": "Introduction",
            "level": 0,
            "content": []
        }
        
        for line in lines:
            # Check if line is a header
            if line.startswith('#'):
                # Save current section if it has content
                if current_section["content"]:
                    sections.append(current_section)
                
                # Create new section
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_section = {
                    "title": title,
                    "level": level,
                    "content": []
                }
            else:
                # Add to current section
                if line.strip():
                    current_section["content"].append(line)
        
        # Add final section
        if current_section["content"]:
            sections.append(current_section)
        
        return sections
    
    def get_document(self, filename: str) -> str:
        """
        Get full document content by filename
        
        Args:
            filename: Name of handbook file (e.g., 'policies.md')
            
        Returns:
            Full content of the file
        """
        return self.documents.get(filename, "")
    
    def get_sections(self, filename: str) -> List[Dict]:
        """
        Get parsed sections from a specific file
        
        Args:
            filename: Name of handbook file
            
        Returns:
            List of sections
        """
        return self.sections.get(filename, [])
    
    def search_text(self, query: str) -> List[Tuple[str, str]]:
        """
        Simple text search (fallback for keyword matching)
        
        Args:
            query: Search term
            
        Returns:
            List of (filename, matching_text) tuples
        """
        results = []
        query_lower = query.lower()
        
        for filename, content in self.documents.items():
            if query_lower in content.lower():
                # Extract surrounding context
                idx = content.lower().find(query_lower)
                start = max(0, idx - 100)
                end = min(len(content), idx + 100)
                context = content[start:end]
                results.append((filename, context))
        
        return results
