"""
Unit tests for the configuration module.
"""
import os
from unittest import TestCase, mock

import pytest

from src.utils.config import Config, SecurityConfig


class TestConfig(TestCase):
    """Test the configuration loading and management."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = Config()
        assert config.DEBUG is False
        assert config.API_PREFIX == "/api/v1"
        assert config.DATABASE.URI == "sqlite:///./taxai.db"
        assert config.AI.MODEL_TYPE == "llama3"

    @mock.patch.dict(os.environ, {"DEBUG": "true"})
    def test_environment_override_bool(self):
        """Test that environment variables override default values for boolean fields."""
        config = Config()
        assert config.DEBUG is True

    @mock.patch.dict(os.environ, {"DATABASE_URI": "postgresql://user:pass@localhost/taxai"})
    def test_environment_override_string(self):
        """Test that environment variables override default values for string fields."""
        config = Config()
        assert config.DATABASE.URI == "postgresql://user:pass@localhost/taxai"

    @mock.patch.dict(os.environ, {"ACCESS_TOKEN_EXPIRE_MINUTES": "60"})
    def test_environment_override_int(self):
        """Test that environment variables override default values for int fields."""
        config = Config()
        assert config.SECURITY.ACCESS_TOKEN_EXPIRE_MINUTES == 60

    @mock.patch.dict(os.environ, {"SECRET_KEY": "test_secret_key"})
    def test_security_config_override(self):
        """Test that environment variables override security configuration."""
        config = Config()
        assert config.SECURITY.SECRET_KEY == "test_secret_key"


class TestSecurityConfig(TestCase):
    """Test the security configuration."""

    def test_default_values(self):
        """Test that default values are set correctly for security configuration."""
        security_config = SecurityConfig()
        assert security_config.ALGORITHM == "HS256"
        assert security_config.ACCESS_TOKEN_EXPIRE_MINUTES == 30
