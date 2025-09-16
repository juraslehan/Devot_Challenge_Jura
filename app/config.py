from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./dev.db"
    JWT_SECRET: str = "dev-secret"
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60
    STARTING_BALANCE: int = 1000

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
