"""Middleware package initialization.

このパッケージにはFlaskアプリケーション用のミドルウェアが含まれています。
"""

from .versioning import APIVersioningMiddleware


__all__ = ["APIVersioningMiddleware"]
