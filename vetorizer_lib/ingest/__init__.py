"""Ingestion utilities for vetorizer_lib.

This module exports functions for ingesting data from various sources.
"""

from vetorizer_lib.ingest.csv import read_csv_batches

__all__ = [
    "read_csv_batches",
]
