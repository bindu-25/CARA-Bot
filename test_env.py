from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

api_key = os.getenv('OPENROUTER_API_KEY')
print(f'API Key loaded: {api_key[:20] if api_key else "NOT FOUND"}...')
