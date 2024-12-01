from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import structlog

logger = structlog.get_logger(__name__)

class Settings(BaseSettings):
    spotify_client_id: str
    spotify_client_secret: str
    log_level: str = "INFO"
    service_name: str = "spotify-translation-service"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='SPOTIFY_',
        case_sensitive=False,
        extra='allow'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info(
            "Settings initialized",
            client_id_set=bool(self.spotify_client_id),
            client_secret_set=bool(self.spotify_client_secret)
        )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
