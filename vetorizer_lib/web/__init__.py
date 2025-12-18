"""Vetorizer Web UI module.

This module provides a web-based graphical interface for managing vector databases,
uploading CSV files, and performing semantic searches.

Usage:
    # Via CLI
    vetorizer serve --port 8000

    # Via Python
    from vetorizer_lib.web import create_app
    app = create_app()
"""

from vetorizer_lib.web.app import create_app

__all__ = ["create_app"]
