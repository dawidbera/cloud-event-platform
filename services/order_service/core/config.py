from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Pydantic BaseSettings class that loads application configuration from environment variables, including database and Kafka connection strings."""
    app_name: str = "Order Service"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # DB
    database_url: str = "postgresql+psycopg2://myuser:mypassword@localhost:5432/cep"
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    consumer_group_id: str = "order-service-group"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
