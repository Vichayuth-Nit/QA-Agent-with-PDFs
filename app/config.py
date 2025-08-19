from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import sys


class Settings(BaseSettings):
    # Define your settings here with type hints
    openai_api_key: str
    temperature: float
    gemini_api_key: str 
    google_api_key: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    collection_name: str

    # This tells Pydantic to look for a .env file
    model_config = SettingsConfigDict(env_file=".env")

# Create a single instance to be used across the app
settings = Settings()

def get_settings():
    return settings

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def get_logger():
    logger = logging.getLogger(__name__)
    return logger
