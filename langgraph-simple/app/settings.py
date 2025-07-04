from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr = SecretStr("")
    OPENAI_MODEL: str = "gpt-4.1"
    FIRECRAWL_API_KEY: SecretStr = SecretStr("")
    FIRECRAWL_API_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
