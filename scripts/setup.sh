#!/bin/bash

echo "Setting up CARA Bot..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please add your API keys."
fi

echo "Setup complete!"
