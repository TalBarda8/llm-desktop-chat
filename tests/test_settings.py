"""
Unit tests for Settings configuration
"""
import pytest
import os
from unittest.mock import patch
from src.config.settings import Settings


class TestSettings:
    """Test cases for Settings class"""

    def test_default_values(self):
        """Test that default values are set correctly"""
        settings = Settings()

        # Ollama API settings
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.default_model == "llama2"

        # UI settings
        assert settings.window_title == "Local LLM Chat"
        assert settings.window_width == 900
        assert settings.window_height == 700

        # Logging settings
        assert settings.log_level == "INFO"
        assert settings.log_file == "logs/app.log"

    def test_custom_ollama_base_url(self):
        """Test setting custom Ollama base URL"""
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://192.168.1.100:11434"}):
            settings = Settings()
            assert settings.ollama_base_url == "http://192.168.1.100:11434"

    def test_custom_default_model(self):
        """Test setting custom default model"""
        with patch.dict(os.environ, {"DEFAULT_MODEL": "mistral"}):
            settings = Settings()
            assert settings.default_model == "mistral"

    def test_custom_window_title(self):
        """Test setting custom window title"""
        with patch.dict(os.environ, {"WINDOW_TITLE": "My LLM Chat"}):
            settings = Settings()
            assert settings.window_title == "My LLM Chat"

    def test_custom_window_dimensions(self):
        """Test setting custom window dimensions"""
        with patch.dict(os.environ, {"WINDOW_WIDTH": "1200", "WINDOW_HEIGHT": "800"}):
            settings = Settings()
            assert settings.window_width == 1200
            assert settings.window_height == 800

    def test_custom_log_level(self):
        """Test setting custom log level"""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            settings = Settings()
            assert settings.log_level == "DEBUG"

    def test_custom_log_file(self):
        """Test setting custom log file path"""
        with patch.dict(os.environ, {"LOG_FILE": "logs/custom.log"}):
            settings = Settings()
            assert settings.log_file == "logs/custom.log"

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case-insensitive"""
        with patch.dict(os.environ, {"ollama_base_url": "http://custom:11434"}):
            settings = Settings()
            assert settings.ollama_base_url == "http://custom:11434"

    def test_multiple_custom_settings(self):
        """Test setting multiple custom values simultaneously"""
        env_vars = {
            "OLLAMA_BASE_URL": "http://custom:11434",
            "DEFAULT_MODEL": "codellama",
            "WINDOW_WIDTH": "1000",
            "LOG_LEVEL": "WARNING"
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.ollama_base_url == "http://custom:11434"
            assert settings.default_model == "codellama"
            assert settings.window_width == 1000
            assert settings.log_level == "WARNING"

    def test_invalid_window_width_type(self):
        """Test that invalid window width type raises error"""
        with patch.dict(os.environ, {"WINDOW_WIDTH": "not_a_number"}):
            with pytest.raises(Exception):  # Pydantic validation error
                Settings()

    def test_invalid_window_height_type(self):
        """Test that invalid window height type raises error"""
        with patch.dict(os.environ, {"WINDOW_HEIGHT": "not_a_number"}):
            with pytest.raises(Exception):  # Pydantic validation error
                Settings()

    def test_settings_mutable_after_creation(self):
        """Test that settings can be modified after creation"""
        settings = Settings()
        original_model = settings.default_model

        # Pydantic models are mutable by default
        settings.default_model = "mistral"
        assert settings.default_model == "mistral"
        assert settings.default_model != original_model


# Run tests with: pytest tests/test_settings.py -v
