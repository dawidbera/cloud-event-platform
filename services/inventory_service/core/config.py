from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Inventory Service"
    app_version: str = "0.1.0"
    debug: bool = False
    
    kafka_bootstrap_servers: str = "localhost:9092"
    consumer_group_id: str = "inventory-service-group"
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
