"""
Unit tests for HR Handbook Chatbot
"""

import pytest
from unittest.mock import Mock, patch

from src.retrieval.loader import HandbookLoader
from src.retrieval.search import SemanticSearch
from src.handlers.chatbot import HRChatbot


class TestHandbookLoader:
    """Tests for HandbookLoader"""
    
    def test_loader_initialization(self):
        """Test loader initializes correctly"""
        loader = HandbookLoader("docs/handbook-content")
        assert loader.handbook_dir == "docs/handbook-content"
    
    def test_load_handbook(self):
        """Test loading handbook files"""
        loader = HandbookLoader("docs/handbook-content")
        documents = loader.load_handbook()
        
        # Should load at least one document
        assert len(documents) > 0
    
    def test_parse_markdown(self):
        """Test markdown parsing"""
        loader = HandbookLoader("docs/handbook-content")
        
        test_content = """# Header 1
        Some text here
        
        ## Header 2
        More text
        """
        
        sections = loader._parse_markdown(test_content)
        assert len(sections) > 0
        assert any("Header" in s["title"] for s in sections)


class TestSemanticSearch:
    """Tests for SemanticSearch"""
    
    def test_search_initialization(self):
        """Test search engine initializes"""
        test_docs = {
            "test.md": "This is a test document about vacation"
        }
        search = SemanticSearch(test_docs)
        assert search.documents == test_docs
    
    def test_keyword_search_fallback(self):
        """Test keyword search fallback"""
        test_docs = {
            "policies.md": "Vacation policy: 20 days per year"
        }
        search = SemanticSearch(test_docs)
        search.client = None  # Disable LLM
        
        results = search._keyword_search("vacation", top_k=1)
        assert len(results) > 0


class TestHRChatbot:
    """Tests for HRChatbot"""
    
    @pytest.fixture
    def mock_search(self):
        """Mock search engine"""
        search = Mock(spec=SemanticSearch)
        search.search.return_value = [
            {
                "filename": "leave.md",
                "text": "You get 20 days of vacation per year",
                "score": 0.9
            }
        ]
        return search
    
    def test_chatbot_initialization(self, mock_search):
        """Test chatbot initializes"""
        chatbot = HRChatbot(mock_search)
        assert chatbot.search_engine == mock_search
    
    def test_escalation_detection(self, mock_search):
        """Test escalation topic detection"""
        chatbot = HRChatbot(mock_search)
        
        assert chatbot._should_escalate("What's my personal salary?")
        assert chatbot._should_escalate("I'm experiencing harassment")
        assert not chatbot._should_escalate("How much vacation do I get?")
    
    def test_process_question_no_results(self, mock_search):
        """Test handling when no search results found"""
        mock_search.search.return_value = []
        chatbot = HRChatbot(mock_search)
        
        response = chatbot.process_question("Random question?")
        
        assert "don't have" in response["answer"].lower()
        assert response["confidence"] == 0.0
    
    def test_escalation_response(self, mock_search):
        """Test escalation response"""
        chatbot = HRChatbot(mock_search)
        response = chatbot._escalation_response("salary question")
        
        assert response["escalation"] is True
        assert "HR" in response["answer"]
    
    def test_conversation_history(self, mock_search):
        """Test conversation history tracking"""
        chatbot = HRChatbot(mock_search)
        
        chatbot.add_to_history("user", "Hello")
        chatbot.add_to_history("assistant", "Hi there")
        
        history = chatbot.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
    
    def test_clear_history(self, mock_search):
        """Test clearing conversation history"""
        chatbot = HRChatbot(mock_search)
        
        chatbot.add_to_history("user", "Test")
        chatbot.clear_history()
        
        assert len(chatbot.get_history()) == 0


class TestIntegration:
    """Integration tests"""
    
    def test_full_question_flow(self):
        """Test complete question flow"""
        # Load handbook
        loader = HandbookLoader("docs/handbook-content")
        documents = loader.load_handbook()
        
        if not documents:
            pytest.skip("No handbook documents available")
        
        # Initialize search
        search = SemanticSearch(documents)
        
        # Initialize chatbot
        chatbot = HRChatbot(search)
        
        # Process a question
        response = chatbot.process_question("How many vacation days do I get?")
        
        # Verify response structure
        assert "answer" in response
        assert "sources" in response
        assert "confidence" in response
        assert isinstance(response["answer"], str)
        assert len(response["answer"]) > 0
