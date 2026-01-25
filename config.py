"""Simplified Configuration"""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

class Settings:
    APP_NAME = "TTS Voice Agent"
    APP_VERSION = "1.0.0"
    DEBUG_MODE = True
    SUPPORTED_LANGUAGES = ["en", "ur"]
    DEFAULT_LANGUAGE = "en"
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_TYPES = [".pdf", ".docx", ".png", ".jpg", ".jpeg"]
    AUDIO_FORMAT = "mp3"
    AUDIO_SAMPLE_RATE = 22050
    ASSETS_DIR = BASE_DIR / "assets"
    LOGS_DIR = BASE_DIR / "logs"
    TEMP_DIR = BASE_DIR / "assets" / "temp"
    TTS_MODE = "auto"
    TTS_TIMEOUT_SECONDS = 5

settings = Settings()

def initialize_directories():
    for directory in [settings.ASSETS_DIR, settings.LOGS_DIR, settings.TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ready: {directory}")

def setup_logging():
    from loguru import logger
    import sys
    logger.remove()
    logger.add(sys.stdout, level="DEBUG", colorize=True)
    logger.add(settings.LOGS_DIR / "app_{time:YYYY-MM-DD}.log", rotation="500 MB", retention="10 days", compression="zip", level="DEBUG")
    return logger

def startup():
    print(f"\n{'='*60}\n🚀 {settings.APP_NAME} v{settings.APP_VERSION}\n{'='*60}\n")
    initialize_directories()
    logger = setup_logging()
    logger.info(f"Application started")
    return logger

if __name__ == "__main__":
    startup()
    print(f"\n✅ Configuration loaded successfully!")