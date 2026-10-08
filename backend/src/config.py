from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    gemini_api_key: str
    bucket_name: str
    redis_url: str
    cors_allowed_origins: str = ""
    action_cooldown_seconds: int = 45
    readonly_database_url: str = ""
    job_search_ro_password: str = ""
    job_search_statement_timeout_seconds: int = 3
    job_search_max_rows: int = 50
    job_search_cooldown_seconds: int = 5
    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

settings = Settings()