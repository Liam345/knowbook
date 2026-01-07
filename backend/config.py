import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
    
    # Application settings
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    PROJECTS_DIR = os.path.join(DATA_DIR, 'projects')
    
    # Ensure data directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PROJECTS_DIR, exist_ok=True)