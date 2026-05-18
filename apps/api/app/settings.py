"""Application settings — environment-driven, validated at startup.

Master Spec §4.4 / §4.5 / §12 — every secret, every feature flag, every
runtime tunable lives here. Settings are loaded from environment variables only
(never from a committed file).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "ci", "staging", "production"]
LlmProvider = Literal["anthropic", "openai", "azure_openai", "bedrock", "gemini", "local"]
LlmMode = Literal["real", "fixture"]
RedactionMode = Literal["strict", "standard", "off"]


class Settings(BaseSettings):
    """Top-level settings object. Read once at process start."""

    model_config = SettingsConfigDict(env_file=None, case_sensitive=False, extra="ignore")

    # Runtime
    environment: Environment = "development"
    log_level: str = "INFO"

    # Database / cache / storage
    database_url: str = "postgresql+psycopg://shield:shield@db:5432/shield"
    redis_url: str = "redis://redis:6379/0"
    s3_endpoint_url: str = "http://minio:9000"
    s3_bucket: str = "shield-artifacts"
    s3_access_key: str = "shield-minio"
    s3_secret_key: str = "shield-minio-secret"
    s3_kms_key_id: str = "dev-stub-key"

    # OIDC / Keycloak
    keycloak_issuer: str = "http://keycloak:8080/realms/shield"
    keycloak_audience: str = "shield-api"

    # LLM
    shield_llm_provider: LlmProvider = "anthropic"
    shield_llm_model: str = "claude-opus-4-7"
    shield_llm_mode: LlmMode = "fixture"
    anthropic_api_key: str = ""

    # Feature flags (deferred for v1)
    shield_auth_require_mfa: bool = False
    shield_auth_require_email_verify: bool = False
    shield_email_delivery_enabled: bool = False

    # Redaction (mandatory primary control per Master Spec §12)
    shield_redaction_mode: RedactionMode = "strict"

    # Session security
    jwt_access_ttl_seconds: int = 900
    jwt_refresh_ttl_seconds: int = 1800
    shield_account_lockout_max_attempts: int = Field(default=10, ge=1)
    shield_account_lockout_window_seconds: int = Field(default=900, ge=60)

    @field_validator("shield_redaction_mode")
    @classmethod
    def _no_redaction_off_outside_dev(cls, v: RedactionMode, info) -> RedactionMode:  # type: ignore[override]
        env = (info.data or {}).get("environment", "development")
        if v == "off" and env != "development":
            raise ValueError(
                "SHIELD_REDACTION_MODE=off is only permitted when ENVIRONMENT=development "
                "(Master Spec §12 — redaction is a security boundary)"
            )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Memoized accessor. Tests should call `get_settings.cache_clear()` between cases."""
    return Settings()  # type: ignore[call-arg]
