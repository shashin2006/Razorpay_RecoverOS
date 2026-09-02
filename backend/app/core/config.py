from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RecoveryOS"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    razorpay_key_id: str
    razorpay_key_secret: str
    razorpay_webhook_secret: str

    # NVIDIA NIM
    nvidia_api_key: str
    nvidia_base_url: str = (
        "https://integrate.api.nvidia.com/v1"
    )
    nvidia_model: str
    nvidia_safety_model: str = (
        "nvidia/nemotron-3.5-content-safety"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()