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
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    MODEL_NAME: str = "groq/deepseek-r1" 
    
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
    
    def validate_settings(self):
        """Validate required settings"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY must be set in environment variables")
        
        if not os.path.exists(self.DATASET_PATH):
            raise ValueError(f"Dataset path does not exist: {self.DATASET_PATH}")

# Create settings instance
settings = Settings()