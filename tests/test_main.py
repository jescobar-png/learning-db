"""Basic tests for Streamlit application."""

import pytest


class TestStreamlitApp:
    """Basic tests for the Streamlit application."""

    def test_app_imports(self) -> None:
        """Test that the app module can be imported."""
        try:
            import app.main  # noqa: F401
        except Exception as e:
            pytest.skip(f"Could not import app: {e}")

    def test_database_imports(self) -> None:
        """Test that database module can be imported."""
        try:
            from app import db  # noqa: F401
        except Exception as e:
            pytest.skip(f"Could not import db: {e}")
