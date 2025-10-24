"""Application package initialization.

This package contains the main Flask application and its components.
"""

from .app import app, socketio  # type: ignore[import-not-found]


__all__ = ["app", "socketio"]
