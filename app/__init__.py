# This file makes the app directory a Python package
from .app import app, socketio

__all__ = ['app', 'socketio']