"""
SAVORIA Backend Configuration
Loads IBM watsonx.ai credentials and application settings from environment variables.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # IBM watsonx.ai configuration
    IBM_API_KEY: str = ""
    IBM_PROJECT_ID: str = ""
    IBM_MODEL_ID: str = "meta-llama/llama-3-3-70b-instruct"
    IBM_WATSONX_URL: str = "https://eu-gb.ml.cloud.ibm.com"
    IBM_IAM_URL: str = "https://iam.cloud.ibm.com/identity/token"

    # Application settings
    APP_NAME: str = "SAVORIA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # RAG settings
    FAISS_INDEX_PATH: str = "data/recipe_index.faiss"
    RECIPE_DATA_PATH: str = "data/recipes.json"
    TOP_K_RETRIEVAL: int = 5
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Generation settings
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
