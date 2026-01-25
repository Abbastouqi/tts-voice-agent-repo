"""
Unit tests for configuration module
"""

import pytest
from config import settings, initialize_directories, startup
from pathlib import Path


def test_settings_loaded():
    """Test that settings are loaded correctly"""
    assert settings.APP_NAME == "TTS Voice Agent"
    assert settings.APP_VERSION == "1.0.0"
    assert "en" in settings.SUPPORTED_LANGUAGES
    assert "ur" in settings.SUPPORTED_LANGUAGES


def test_directories_exist():
    """Test that required directories are created"""
    initialize_directories()
    
    assert settings.ASSETS_DIR.exists()
    assert settings.LOGS_DIR.exists()
    assert settings.TEMP_DIR.exists()


def test_supported_languages():
    """Test language configuration"""
    assert len(settings.SUPPORTED_LANGUAGES) == 2
    assert settings.DEFAULT_LANGUAGE in settings.SUPPORTED_LANGUAGES


def test_file_upload_limits():
    """Test file upload constraints"""
    assert settings.MAX_FILE_SIZE_MB > 0
    assert len(settings.ALLOWED_FILE_TYPES) > 0
    assert ".pdf" in settings.ALLOWED_FILE_TYPES


if __name__ == "__main__":
    pytest.main([__file__, "-v"])