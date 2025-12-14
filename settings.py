from pydantic_settings import BaseSettings, SettingsConfigDict
import asyncpg


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_DB: str

    MONGO_ROOT_USER: str
    MONGO_ROOT_PASS: str
    MONGO_APP_USER: str
    MONGO_APP_PASS: str
    MONGO_DB: str

    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASS: str
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    APP_PORT: int

    @property
    def DATABASE_ASYNC_URL(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DB}'
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()