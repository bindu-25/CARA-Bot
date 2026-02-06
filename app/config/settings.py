from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "CARA Bot"
    VERSION: str = "1.0.0"
    
    # API keys
    OPENROUTER_API_KEY: str = ""  # Changed from ANTHROPIC_API_KEY
    
    # OpenRouter settings
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "anthropic/claude-sonnet-4-20250514"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = DATA_DIR / "models"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    
    # Model settings
    MAX_TEXT_LENGTH: int = 100000
    
    class Config:
        env_file = ".env"