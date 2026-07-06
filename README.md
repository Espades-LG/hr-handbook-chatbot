# HR Handbook Chatbot

An intelligent chatbot that answers employee questions about HR policies, benefits, compensation, and procedures using the company HR handbook.

## Features

- **Semantic Search**: Uses AI embeddings to find relevant handbook content
- **Intelligent Responses**: LLM-powered responses based on handbook information
- **Escalation Handling**: Routes sensitive questions to HR team
- **Conversation History**: Tracks conversation context
- **Easy Customization**: Built on company handbook markdown files

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (for LLM features)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/[your-org]/hr-handbook-chatbot.git
   cd hr-handbook-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the chatbot**
   ```bash
   python -m src.main
   ```

## Usage

### Interactive Mode

```bash
python -m src.main
```

Then ask questions like:
- "How many vacation days do I get?"
- "What's the 401(k) match?"
- "How do I request time off?"

### Programmatic Usage

```python
from src.main import ChatbotApplication

app = ChatbotApplication()
response = app.chat("How many vacation days do I get?")
print(response["answer"])
print(f"Source: {response['sources']}")
```

## Project Structure

```
hr-handbook-chatbot/
├── docs/
│   ├── handbook-content/     # HR handbook markdown files
│   │   ├── policies.md
│   │   ├── benefits.md
│   │   ├── leave.md
│   │   ├── compensation.md
│   │   └── other.md
│   └── chatbot-spec.md       # Chatbot specification
├── src/
│   ├── main.py               # Entry point
│   ├── config/               # Configuration
│   ├── handlers/
│   │   └── chatbot.py        # Chatbot logic
│   └── retrieval/
│       ├── loader.py         # Handbook loader
│       └── search.py         # Semantic search
├── tests/                    # Unit tests
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## How It Works

1. **Handbook Loading** (`src/retrieval/loader.py`)
   - Reads all markdown files from `docs/handbook-content/`
   - Parses content into sections and chunks

2. **Semantic Search** (`src/retrieval/search.py`)
   - Creates embeddings for all handbook content
   - Finds relevant sections based on user questions
   - Ranks results by relevance

3. **Response Generation** (`src/handlers/chatbot.py`)
   - Takes relevant handbook content
   - Uses LLM to generate natural language responses
   - Cites sources and escalates when needed

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Configuration

Edit `.env` to customize:

```
OPENAI_API_KEY=your-key-here      # Required for LLM features
OPENAI_MODEL=gpt-4                # Can use gpt-3.5-turbo, gpt-4, etc.
DEBUG=False                        # Set to True for verbose logging
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
HANDBOOK_DIR=docs/handbook-content # Path to handbook files
```

## Adding/Updating Handbook Content

1. Edit markdown files in `docs/handbook-content/`
2. Follow the structure in `docs/chatbot-spec.md`
3. Commit changes to a branch
4. Submit a pull request for review
5. Tests run automatically via GitHub Actions

## Integrations

### Slack (Future)
```python
from slack_bolt import App
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message(".*")
def respond(message, say):
    chatbot = ChatbotApplication().get_chatbot()
    response = chatbot.process_question(message["text"])
    say(response["answer"])
```

### Microsoft Teams (Future)
[Instructions for Teams integration]

### Web Interface (Future)
[Instructions for web UI]

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write/update tests
4. Commit with descriptive messages
5. Push to your branch
6. Open a Pull Request

## Testing Changes

Before submitting a PR:
- Run tests: `pytest tests/ -v`
- Check code style: `black --check src tests`
- Lint: `flake8 src tests`

## Architecture Decisions

- **Python**: Easy to maintain, rich ML/NLP libraries
- **LangChain**: Simplified LLM orchestration
- **OpenAI API**: Powerful embeddings and LLM access
- **Markdown for handbook**: Version control friendly, readable, no database needed

## Limitations

- Responses based only on handbook content
- No access to real-time data (benefits balances, claim status)
- Cannot make decisions or approve exceptions
- Escalates sensitive matters to HR

## Roadmap

- [ ] Multi-language support
- [ ] Slack/Teams integration
- [ ] Web dashboard
- [ ] Analytics on common questions
- [ ] Feedback loop for continuous improvement
- [ ] Support for multiple LLM providers

## Troubleshooting

### "No handbook documents loaded"
- Check that `docs/handbook-content/` exists
- Verify markdown files are present
- Check file permissions

### "OpenAI API error"
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid
- Verify you have available API credits

### "Search results not relevant"
- Try rephrasing your question
- Check that handbook covers the topic
- Review `SIMILARITY_THRESHOLD` in config

## Support

- **Questions?** Email: hr@company.com
- **Report bugs:** Open an issue on GitHub
- **Suggestions:** Discuss in pull requests

## License

[Your License Here - e.g., MIT]

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenAI](https://openai.com)
- [Pydantic](https://docs.pydantic.dev/)
