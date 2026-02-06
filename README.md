# CARA Bot - Contract Analysis & Risk Assessment

AI-powered legal assistant for analyzing contracts, assessing risks, and checking compliance with Indian laws.

## Features

- **Contract Analysis**: Extract parties, dates, amounts, and key clauses
- **Risk Assessment**: Identify and score legal, financial, and compliance risks
- **Compliance Check**: Verify compliance with Indian laws
- **Template Generation**: Generate standard contract templates

## Quick Start

### Get OpenRouter API Key

1. Sign up at https://openrouter.ai/
2. Get your API key from https://openrouter.ai/keys
3. Add credits to your account

### Installation
```bash
# Clone repository
cd CARA-Bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Configuration

Create `.env` file:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
```

### Download Datasets
```bash
python scripts/download_data.py
```

### Run Application

**Streamlit UI:**
```bash
streamlit run app/main.py
```

**API Server:**
```bash
uvicorn app.api.endpoints:app --reload
```

## Available Models via OpenRouter

You can use any model available on OpenRouter:
- `anthropic/claude-sonnet-4-20250514` (default)
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4-turbo`
- `meta-llama/llama-3.1-70b-instruct`

Change in `.env`:
```
DEFAULT_MODEL=openai/gpt-4-turbo
```

## Cost Estimates

Using Claude Sonnet 4 via OpenRouter:
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens
- Typical contract analysis: $0.05-0.20 per contract

## License

MIT License