"""Command-line interface for the Vetorizer web server.

This module provides CLI commands to start and manage the web UI server.

Usage:
    # Start the web server
    vetorizer serve --port 8000

    # Or via Python module
    python -m vetorizer_lib.web.cli serve --port 8000

    # With configuration options
    vetorizer serve --qdrant-path ./my-data --embedding-model sentence-transformers/all-MiniLM-L6-v2
"""

import argparse
import os
import sys
from typing import Optional


def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    qdrant_url: str | None = None,
    qdrant_api_key: str | None = None,
    qdrant_path: str | None = None,
    embedding_model: str | None = None,
    max_upload_size: int | None = None,
) -> None:
    """Start the Vetorizer web server.

    Args:
        host: Host address to bind to.
        port: Port number to listen on.
        reload: Enable auto-reload for development.
        qdrant_url: URL for remote Qdrant server (e.g., http://localhost:6333).
        qdrant_api_key: API key for Qdrant Cloud.
        qdrant_path: Path to Qdrant file-based storage (used if qdrant_url not set).
        embedding_model: Default embedding model name.
        max_upload_size: Maximum file upload size in bytes.

    Example:
        >>> serve(host="0.0.0.0", port=8080)
    """
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required. Install with: pip install uvicorn[standard]")
        sys.exit(1)

    # Set environment variables for configuration overrides
    if qdrant_url is not None:
        os.environ["VETORIZER_QDRANT_URL"] = qdrant_url
    if qdrant_api_key is not None:
        os.environ["VETORIZER_QDRANT_API_KEY"] = qdrant_api_key
    if qdrant_path is not None:
        os.environ["VETORIZER_QDRANT_PATH"] = qdrant_path
    if embedding_model is not None:
        os.environ["VETORIZER_EMBEDDING_MODEL"] = embedding_model
    if max_upload_size is not None:
        os.environ["VETORIZER_MAX_UPLOAD_SIZE"] = str(max_upload_size)
    os.environ["VETORIZER_HOST"] = host
    os.environ["VETORIZER_PORT"] = str(port)

    print(f"Starting Vetorizer Web UI at http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/api/docs")
    if qdrant_url:
        print(f"Qdrant server: {qdrant_url}")
    elif qdrant_path:
        print(f"Qdrant storage: {qdrant_path}")
    else:
        print("Qdrant storage: ./data/qdrant (default)")
    if embedding_model:
        print(f"Default embedding model: {embedding_model}")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(
        "vetorizer_lib.web.app:app",
        host=host,
        port=port,
        reload=reload,
    )


def main(args: Optional[list[str]] = None) -> None:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments. If None, uses sys.argv.
    """
    parser = argparse.ArgumentParser(
        prog="vetorizer",
        description="Vetorizer - Vector database management CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the web UI server",
    )
    serve_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number to listen on (default: 8000)",
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    serve_parser.add_argument(
        "--qdrant-url",
        type=str,
        default=None,
        help="URL for remote Qdrant server (e.g., http://localhost:6333)",
    )
    serve_parser.add_argument(
        "--qdrant-api-key",
        type=str,
        default=None,
        help="API key for Qdrant Cloud (optional)",
    )
    serve_parser.add_argument(
        "--qdrant-path",
        type=str,
        default=None,
        help="Path to Qdrant file-based storage (default: ./data/qdrant, ignored if --qdrant-url is set)",
    )
    serve_parser.add_argument(
        "--embedding-model",
        type=str,
        default=None,
        help="Default embedding model name (default: sentence-transformers/all-MiniLM-L6-v2)",
    )
    serve_parser.add_argument(
        "--max-upload-size",
        type=int,
        default=None,
        help="Maximum file upload size in bytes (default: 104857600 = 100MB)",
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "serve":
        serve(
            host=parsed_args.host,
            port=parsed_args.port,
            reload=parsed_args.reload,
            qdrant_url=parsed_args.qdrant_url,
            qdrant_api_key=parsed_args.qdrant_api_key,
            qdrant_path=parsed_args.qdrant_path,
            embedding_model=parsed_args.embedding_model,
            max_upload_size=parsed_args.max_upload_size,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
