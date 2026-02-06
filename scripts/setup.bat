@echo off

echo Setting up CARA Bot...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM Download spaCy model
python -m spacy download en_core_web_sm

REM Create .env file
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please add your API keys.
)

echo Setup complete!
