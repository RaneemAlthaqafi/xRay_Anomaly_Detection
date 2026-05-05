from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    MODEL_PATH: Path = Path("/app/weights/best.onnx")
    CONF_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.45
    IMG_SIZE: int = 640

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    FONT_PATH: Path = Path(__file__).resolve().parent.parent / "fonts" / "NotoNaskhArabic-Regular.ttf"

    MAX_UPLOAD_MB: int = 10

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
