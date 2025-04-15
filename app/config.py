from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Clear AI Backend"

    # MongoDB Settings
    MONGODB_URI: str
    MONGODB_DB_NAME: str

    class Config:
        """Pydantic configuration class."""

        case_sensitive = True
        env_file = ".env"


settings = Settings()
