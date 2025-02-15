from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Finance Audit LLM"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./finance_audit.db"
    
    # Dataset Settings
    DATASET_PATH: str = os.path.join(os.getcwd(), "LLMDataset")
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    MODEL_NAME: str = "gpt-4"  # or another model of choice
    
    # Agent Settings
    ENABLE_AGENT_LOGGING: bool = True
    MAX_TOKENS_PER_RESPONSE: int = 2000
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    @property
    def api_settings(self):
        """Get API-specific settings"""
        return {
            "title": self.APP_NAME,
            "version": self.APP_VERSION,
            "debug": self.DEBUG
        }
    
    @property
    def llm_settings(self):
        """Get LLM-specific settings"""
        return {
            "model_name": self.MODEL_NAME,
            "api_key": self.OPENAI_API_KEY,
            "max_tokens": self.MAX_TOKENS_PER_RESPONSE
        }
    
    @property
    def database_settings(self):
        """Get database-specific settings"""
        return {
            "url": self.DATABASE_URL
        }
    
    def validate_settings(self):
        """Validate required settings"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        if not os.path.exists(self.DATASET_PATH):
            raise ValueError(f"Dataset path does not exist: {self.DATASET_PATH}")

# Create settings instance
settings = Settings()