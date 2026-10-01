from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Validates and holds all application settings, pulling values from environment variables or a .env file."""
    app_name: str = "Payment Service"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    consumer_group_id: str = "payment-service-group"
    
    # Optional DB/Redis for idempotency later
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
