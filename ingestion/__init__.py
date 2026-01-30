"""Ingestion package - Data loading and validation."""
from .loader import MovieDataLoader, create_sample_dataset

__all__ = ['MovieDataLoader', 'create_sample_dataset']
