"""
HR Handbook Chatbot
Main entry point for the application
"""

import logging
import sys
from pathlib import Path

from src.config import HANDBOOK_DIR, LOG_LEVEL, LOG_FORMAT
from src.retrieval.loader import HandbookLoader
from src.retrieval.search import SemanticSearch
from src.handlers.chatbot import HRChatbot

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


class ChatbotApplication:
    """Main chatbot application"""
    
    def __init__(self):
        """Initialize the chatbot application"""
        logger.info("Initializing HR Handbook Chatbot...")
        
        # Load handbook
        self.loader = HandbookLoader(HANDBOOK_DIR)
        documents = self.loader.load_handbook()
        
        if not documents:
            logger.error("No handbook documents loaded!")
            sys.exit(1)
        
        logger.info(f"Loaded {len(documents)} handbook documents")
        
        # Initialize search
        self.search_engine = SemanticSearch(documents)
        
        # Initialize chatbot
        self.chatbot = HRChatbot(self.search_engine)
        
        logger.info("Chatbot initialized successfully")
    
    def chat(self, user_input: str) -> Dict:
        """
        Process user input and return chatbot response
        
        Args:
            user_input: User's question
            
        Returns:
            Chatbot response
        """
        logger.info(f"User: {user_input}")
        
        # Get response from chatbot
        response = self.chatbot.process_question(user_input)
        
        # Add to history
        self.chatbot.add_to_history("user", user_input)
        self.chatbot.add_to_history("assistant", response["answer"])
        
        logger.info(f"Response: {response['answer'][:100]}...")
        
        return response
    
    def interactive_mode(self):
        """Run chatbot in interactive mode"""
        print("\n" + "="*60)
        print("HR HANDBOOK CHATBOT")
        print("="*60)
        print("Ask me questions about HR policies, benefits, leave, etc.")
        print("Type 'exit' or 'quit' to stop.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\nThank you for using HR Handbook Chatbot!")
                    break
                
                response = self.chat(user_input)
                
                print(f"\nChatbot: {response['answer']}\n")
                
                if response.get("sources"):
                    print(f"Sources: {', '.join(response['sources'])}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"An error occurred: {e}\n")
    
    def get_chatbot(self) -> HRChatbot:
        """Get the chatbot instance for external use"""
        return self.chatbot


def main():
    """Main entry point"""
    app = ChatbotApplication()
    app.interactive_mode()


if __name__ == "__main__":
    main()
