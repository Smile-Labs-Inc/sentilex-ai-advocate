"""
Configuration Settings for SentiLex AI Advocate

Loads environment variables and provides typed settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    DB_DRIVER: str = os.getenv("DB_DRIVER", "mysql+pymysql")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "sentilex")
    SQL_ECHO: bool = os.getenv("SQL_ECHO", "false").lower() in ("1", "true", "yes")
    
    # AWS S3 Evidence Storage Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "sentilex-evidence-vault-2026")
    S3_SIGNATURE_VERSION: str = "s3v4"  # Use AWS Signature Version 4
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() in ("1", "true", "yes")
    
    # Audit Logging
    AUDIT_LOG_DIR: str = os.getenv("AUDIT_LOG_DIR", "logs")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # MCP Service
    MCP_HOST: str = os.getenv("MCP_HOST", "localhost")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "3000"))
    
    # LangSmith (Optional)
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() in ("1", "true", "yes")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "sentilex-ai-advocate")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "12"))
    PASSWORD_REQUIRE_SPECIAL: bool = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() in ("1", "true", "yes")
    PASSWORD_REQUIRE_UPPERCASE: bool = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() in ("1", "true", "yes")
    PASSWORD_REQUIRE_NUMBER: bool = os.getenv("PASSWORD_REQUIRE_NUMBER", "true").lower() in ("1", "true", "yes")
    PASSWORD_HISTORY_COUNT: int = int(os.getenv("PASSWORD_HISTORY_COUNT", "5"))
    
    # Account Security
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = int(os.getenv("ACCOUNT_LOCKOUT_DURATION_MINUTES", "30"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    MAX_CONCURRENT_SESSIONS: int = int(os.getenv("MAX_CONCURRENT_SESSIONS", "3"))
    MAX_CONCURRENT_SESSIONS_LAWYER: int = int(os.getenv("MAX_CONCURRENT_SESSIONS_LAWYER", "5"))
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@sentilex.lk")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "SentiLex AI Advocate")
    
    # Multi-Factor Authentication
    MFA_ISSUER_NAME: str = os.getenv("MFA_ISSUER_NAME", "SentiLex")
    MFA_BACKUP_CODES_COUNT: int = int(os.getenv("MFA_BACKUP_CODES_COUNT", "10"))
    MFA_MANDATORY_FOR_ADMINS: bool = os.getenv("MFA_MANDATORY_FOR_ADMINS", "true").lower() in ("1", "true", "yes")
    
    # Security Settings
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    ENABLE_HTTPS_REDIRECT: bool = os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower() in ("1", "true", "yes")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() in ("1", "true", "yes")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Oauth (Google)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")





    


# Singleton instance
settings = Settings()
