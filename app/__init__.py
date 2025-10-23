"""Application package initialization.

This package contains the main Flask application and its components.
"""

from .app import app, socketio


__all__ = ["app", "socketio"]
