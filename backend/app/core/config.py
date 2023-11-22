import enum
import secrets
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    OTP_EXPIRE_MINUTES: int = 15
    SERVER_NAME: str = "serenity.health"
    SERVER_HOST: AnyHttpUrl = "http://api.serenity.health"
    CLIENT_APP_HOST: Optional[AnyHttpUrl] = "https://app.serenity.health"
    CLIENT_APP_PASSWORD_RESET_URL: Optional[
        AnyHttpUrl
    ] = "https://app.serenity.health/auth/reset-password"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    DEFAULT_TRANSACTION_FEE: Decimal = Decimal("0.05")

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    HUBTEL_CLIENT_ID: Optional[str] = ""
    HUBTEL_CLIENT_SECRET: Optional[str] = ""
    HUBTEL_SMS_BASE_URL: Optional[str] = "https://smsc.hubtel.com/v1"
    HUBTEL_FROM_ADDRESS: Optional[str] = "Serenity Health"
    MAILGUN_BASE_URL: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = None
    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    PAYSTACK_BASE_URL: str = "https://api.paystack.co"
    PAYSTACK_SECRET_KEY: str

    SENDGRID_API_KEY: Optional[str] = None

    PATIENT_PORTAL_POSTGRES_SERVER: str
    PATIENT_PORTAL_POSTGRES_USER: str
    PATIENT_PORTAL_POSTGRES_PASSWORD: str
    PATIENT_PORTAL_POSTGRES_DB: str
    PATIENT_PORTAL_SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    PATIENT_PORTAL_SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("PATIENT_PORTAL_SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_patient_portal_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("PATIENT_PORTAL_POSTGRES_USER"),
            password=values.get("PATIENT_PORTAL_POSTGRES_PASSWORD"),
            host=values.get("PATIENT_PORTAL_POSTGRES_SERVER"),
            path=f"/{values.get('PATIENT_PORTAL_POSTGRES_DB') or ''}",
            port="5432",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False
    EMAIL_OTP_TEMPLATE_ID: str = "otp_verification_code"
    PASSWORD_RESET_TEMPLATE_ID: str = "password_reset_email"

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False
    SEGMENT_WRITE_KEY: Optional[
        str
    ] = None  # TODO: Implement: https://segment.com/docs/connections/sources/catalog/libraries/server/python/quickstart/
    TWILIO_ACCOUNT_SID: Optional[str] = ""
    TWILIO_AUTH_TOKEN: Optional[str] = ""
    TWILIO_MESSAGING_SERVICE_SID: Optional[str] = ""

    class Config:
        case_sensitive = True


class OAuthScopeType(str, enum.Enum):
    READ_CURRENT_USER = "current_user:read"
    WRITE_CURRENT_USER = "current_user:write"
    READ_USERS = "users:read"
    WRITE_USER_OAUTH2_SCOPE = "user_oauth2_scope:write"


settings = Settings()
# ensure that transaction fees are always 5% by default
settings.DEFAULT_TRANSACTION_FEE = Decimal(5.00)


OAuth2Scopes = {
    OAuthScopeType.READ_CURRENT_USER.value: "Read information about the current authenticated user",
    OAuthScopeType.READ_USERS.value: "Read information about all users",
    OAuthScopeType.WRITE_CURRENT_USER.value: "Read information about all users",
    OAuthScopeType.WRITE_USER_OAUTH2_SCOPE: "Write oauth scopes for other users",
}
