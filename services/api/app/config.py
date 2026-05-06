from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    MODEL_PATH: Path = Path("/app/weights/best.onnx")
    INFERENCE_PROVIDER: str = "local"
    CONF_THRESHOLD: float = 0.20
    IOU_THRESHOLD: float = 0.45
    IMG_SIZE: int = 640

    ROBOFLOW_API_KEY: str = ""
    ROBOFLOW_MODEL_ID: str = "x-ray-baggage-rkyb4/3"
    ROBOFLOW_API_BASE: str = "https://serverless.roboflow.com"

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    FONT_PATH: Path = Path(__file__).resolve().parent.parent / "fonts" / "NotoNaskhArabic-Regular.ttf"

    MAX_UPLOAD_MB: int = 10

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def effective_model_path(self) -> Path:
        if self.MODEL_PATH.exists():
            return self.MODEL_PATH

        repo_root = Path(__file__).resolve().parents[3]
        candidates = [
            repo_root / "data" / "weights" / self.MODEL_PATH.name,
            repo_root / self.MODEL_PATH.name,
            Path.cwd() / "data" / "weights" / self.MODEL_PATH.name,
            Path.cwd() / self.MODEL_PATH.name,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        return self.MODEL_PATH


settings = Settings()
