from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "DynamicBuilds Pvt. Ltd."
    secret_key: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
    database_url: str = "sqlite:///./dynamicbuilds.db"
    base_url: str = "http://127.0.0.1:8000"
    resend_api_key: str = ""
    email_from: str = "DynamicBuilds <onboarding@resend.dev>"
    company_email: str = "patelrohit52525@gmail.com"
    company_phone: str = "+918252042824"
    upload_dir: str = "static/uploads"
    max_upload_mb: int = 8
    secure_cookies: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
