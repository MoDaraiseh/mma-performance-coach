"""Validated deployment settings; local defaults never imply production readiness."""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
        hide_input_in_errors=True,
    )
    app_env: str = "development"
    cookie_secure: bool = False
    public_origin: str = ""
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    session_hours: int = Field(24, ge=1, le=720)
    api_per_minute: int = Field(600, ge=1, le=100000)
    auth_per_minute: int = Field(10, ge=1, le=1000)
    ai_per_day: int = Field(20, ge=1, le=10000)
    max_body_bytes: int = Field(131072, ge=4096, le=1048576)
    conversation_retention_days: int = Field(30, ge=1, le=3650)
    draft_retention_days: int = Field(30, ge=1, le=3650)
    log_level: str = "INFO"
    identity_mode: Literal["local", "oidc"] = "local"
    oidc_issuer: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_state_secret: str = ""
    allow_legacy_recovery: bool = True
    retention_enabled: bool = False
    ai_global_daily: int = Field(1000, ge=0, le=1000000)
    ai_global_monthly: int = Field(10000, ge=0, le=10000000)
    ai_allowed_models: str = "gpt-4o-mini"
    ai_max_output_tokens: int = Field(1100, ge=256, le=4096)
    ai_max_context_chars: int = Field(16000, ge=2000, le=16000)
    ai_input_usd_per_million: float = Field(0, ge=0, le=1000)
    ai_output_usd_per_million: float = Field(0, ge=0, le=10000)

    @model_validator(mode="after")
    def production(self):
        if self.app_env not in {"development", "test", "production"}:
            raise ValueError("APP_ENV must be development, test or production")
        if self.app_env == "production":
            origin = urlsplit(self.public_origin)
            if not self.cookie_secure or origin.scheme != "https" or not origin.hostname:
                raise ValueError("Production requires secure cookies and HTTPS PUBLIC_ORIGIN")
            if origin.path or origin.query or origin.fragment or origin.username or origin.password:
                raise ValueError("PUBLIC_ORIGIN must be an origin without path or credentials")
            hosts = [s.strip() for s in self.allowed_hosts.split(",")]
            if "*" in hosts or origin.hostname not in hosts:
                raise ValueError("Production requires explicit matching ALLOWED_HOSTS")
            if self.identity_mode != "oidc":
                raise ValueError("Production requires configured managed OIDC identity")
        if self.identity_mode == "oidc":
            issuer = urlsplit(self.oidc_issuer)
            if (
                issuer.scheme != "https"
                or not issuer.hostname
                or issuer.query
                or issuer.fragment
                or issuer.username
                or issuer.password
            ):
                raise ValueError("OIDC_ISSUER must be a trusted HTTPS issuer URL")
            if (
                not self.oidc_client_id
                or not self.oidc_client_secret
                or len(self.oidc_state_secret) < 32
            ):
                raise ValueError(
                    "OIDC requires client credentials and a shared state secret of at least 32 characters"
                )
        return self


settings = Settings()
