"""
Movie data model - Canonical schema for the recommendation system.
All ML logic operates on Movie objects, not raw DataFrames.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Movie:
    """
    Canonical representation of a movie entity.
    
    This schema ensures type safety and consistency across the pipeline.
    """
    movie_id: int
    title: str
    genres: List[str]
    overview: str
    language: str
    rating: float
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Ensure genres is a list
        if isinstance(self.genres, str):
            self.genres = [g.strip() for g in self.genres.split(',') if g.strip()]
        
        # Normalize language code
        self.language = self.language.lower() if self.language else 'unknown'
        
        # Ensure rating is within bounds
        if self.rating < 0 or self.rating > 10:
            self.rating = 0.0
    
    def __repr__(self) -> str:
        return f"Movie(id={self.movie_id}, title='{self.title}', genres={self.genres})"
    
    def to_dict(self) -> Dict:
        """Convert Movie object to dictionary for serialization."""
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'genres': self.genres,
            'overview': self.overview,
            'language': self.language,
            'rating': self.rating,
            'metadata': self.metadata
        }
