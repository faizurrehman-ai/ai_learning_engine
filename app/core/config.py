from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ezitech AI Learning Engine"
    API_V1_STR: str = "/api/v1"

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "neo4j"

    DATABASE_URL: str = "sqlite:///./learning_engine.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()