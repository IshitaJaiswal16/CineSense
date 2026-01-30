"""
Preference Engine Module - THE DIFFERENTIATOR
Responsibilities:
- Apply user preferences to re-rank recommendations
- Soft weighting (no hard filters)
- Boost scores based on genre/language matches

This is what makes the system personalized and production-like.
"""
from typing import List, Tuple, Dict, Optional
import logging

from models.movie import Movie

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserPreferences:
    """
    Encapsulates user preferences for personalization.
    """
    
    def __init__(
        self,
        preferred_genres: List[str] = None,
        preferred_languages: List[str] = None,
        genre_weight: float = 0.3,
        language_weight: float = 0.2,
        min_rating: float = 0.0
    ):
        """
        Initialize user preferences.
        
        Args:
            preferred_genres: List of preferred genres
            preferred_languages: List of preferred language codes
            genre_weight: Weight multiplier for genre matches
            language_weight: Weight multiplier for language matches
            min_rating: Minimum acceptable rating (soft filter)
        """
        self.preferred_genres = set(preferred_genres or [])
        self.preferred_languages = set(preferred_languages or [])
        self.genre_weight = genre_weight
        self.language_weight = language_weight
        self.min_rating = min_rating
    
    def __repr__(self) -> str:
        return (
            f"UserPreferences(genres={list(self.preferred_genres)}, "
            f"languages={list(self.preferred_languages)})"
        )


class PreferenceEngine:
    """
    Re-ranks recommendations based on user preferences.
    Uses soft weighting to boost relevant items without hard filtering.
    """
    
    def __init__(self, movies: List[Movie]):
        """
        Initialize the preference engine.
        
        Args:
            movies: List of all Movie objects (for metadata lookup)
        """
        self.movies_by_id = {movie.movie_id: movie for movie in movies}
        logger.info(f"Preference engine initialized with {len(movies)} movies")
    
    def _compute_genre_boost(
        self,
        movie: Movie,
        preferences: UserPreferences
    ) -> float:
        """
        Compute boost factor based on genre overlap.
        
        Args:
            movie: Movie to evaluate
            preferences: User preferences
            
        Returns:
            Boost factor (0 to 1)
        """
        if not preferences.preferred_genres:
            return 0.0
        
        # Calculate genre overlap
        movie_genres = set(movie.genres)
        overlap = len(movie_genres & preferences.preferred_genres)
        max_possible = len(preferences.preferred_genres)
        
        # Normalize to 0-1
        genre_match_score = overlap / max_possible if max_possible > 0 else 0.0
        
        return genre_match_score * preferences.genre_weight
    
    def _compute_language_boost(
        self,
        movie: Movie,
        preferences: UserPreferences
    ) -> float:
        """
        Compute boost factor based on language match.
        
        Args:
            movie: Movie to evaluate
            preferences: User preferences
            
        Returns:
            Boost factor (0 or language_weight)
        """
        if not preferences.preferred_languages:
            return 0.0
        
        if movie.language in preferences.preferred_languages:
            return preferences.language_weight
        
        return 0.0
    
    def _compute_rating_penalty(
        self,
        movie: Movie,
        preferences: UserPreferences
    ) -> float:
        """
        Compute penalty for low-rated movies (soft filter).
        
        Args:
            movie: Movie to evaluate
            preferences: User preferences
            
        Returns:
            Penalty factor (0 to 1, where 1 = no penalty)
        """
        if movie.rating >= preferences.min_rating:
            return 1.0
        
        # Soft penalty for movies below min rating
        # Still allows them but reduces their score
        ratio = movie.rating / preferences.min_rating if preferences.min_rating > 0 else 1.0
        return max(0.5, ratio)  # Minimum 50% penalty
    
    def apply_preferences(
        self,
        candidates: List[Tuple[int, float]],
        preferences: UserPreferences,
        normalize: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Re-rank candidates based on user preferences.
        
        Args:
            candidates: List of (movie_id, score) tuples from similarity engine
            preferences: User preferences to apply
            normalize: Whether to normalize final scores to 0-1
            
        Returns:
            Re-ranked list of (movie_id, adjusted_score) tuples
        """
        logger.info("Applying user preferences...")
        
        adjusted_candidates = []
        
        for movie_id, base_score in candidates:
            # Get movie metadata
            movie = self.movies_by_id.get(movie_id)
            if not movie:
                logger.warning(f"Movie ID {movie_id} not found, skipping")
                continue
            
            # Compute boosts
            genre_boost = self._compute_genre_boost(movie, preferences)
            language_boost = self._compute_language_boost(movie, preferences)
            rating_penalty = self._compute_rating_penalty(movie, preferences)
            
            # Combine: base score + boosts, then apply penalty
            adjusted_score = (base_score + genre_boost + language_boost) * rating_penalty
            
            adjusted_candidates.append((movie_id, adjusted_score))
        
        # Sort by adjusted score
        adjusted_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Optional normalization
        if normalize and adjusted_candidates:
            max_score = max(score for _, score in adjusted_candidates)
            if max_score > 0:
                adjusted_candidates = [
                    (mid, score / max_score) for mid, score in adjusted_candidates
                ]
        
        logger.info(f"✓ Re-ranked {len(adjusted_candidates)} candidates")
        return adjusted_candidates
    
    def filter_and_rank(
        self,
        candidates: List[Tuple[int, float]],
        preferences: UserPreferences,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Apply preferences and return enriched results.
        
        Args:
            candidates: List of (movie_id, score) tuples
            preferences: User preferences
            top_k: Number of results to return
            
        Returns:
            List of dicts with movie info and scores
        """
        # Apply preferences
        ranked = self.apply_preferences(candidates, preferences)
        
        # Take top-k
        top_results = ranked[:top_k]
        
        # Enrich with metadata
        enriched_results = []
        for movie_id, score in top_results:
            movie = self.movies_by_id[movie_id]
            enriched_results.append({
                'movie_id': movie_id,
                'title': movie.title,
                'genres': movie.genres,
                'language': movie.language,
                'rating': movie.rating,
                'overview': movie.overview,
                'score': score,
                'metadata': movie.metadata
            })
        
        return enriched_results


if __name__ == "__main__":
    # Example usage
    from ingestion.loader import MovieDataLoader, create_sample_dataset
    from features.feature_builder import FeatureBuilder
    from similarity.similarity_engine import SimilarityEngine
    
    # Setup
    create_sample_dataset()
    loader = MovieDataLoader('data/movies.csv')
    movies = loader.load()
    
    builder = FeatureBuilder()
    feature_matrix = builder.build_features(movies)
    
    engine = SimilarityEngine(feature_matrix)
    
    # Get similar movies
    query_movie = movies[0]  # The Matrix
    query_idx = builder.get_movie_index(query_movie.movie_id)
    similar = engine.find_similar_items(query_idx, top_k=10)
    
    # Convert to movie IDs
    candidates = [(builder.get_movie_id(idx), score) for idx, score in similar]
    
    # Apply preferences
    preferences = UserPreferences(
        preferred_genres=['Action', 'Sci-Fi'],
        preferred_languages=['en'],
        genre_weight=0.4,
        language_weight=0.1,
        min_rating=7.0
    )
    
    pref_engine = PreferenceEngine(movies)
    results = pref_engine.filter_and_rank(candidates, preferences, top_k=5)
    
    print(f"\n{'='*60}")
    print(f"Recommendations for '{query_movie.title}' with preferences:")
    print(f"  Preferred genres: {list(preferences.preferred_genres)}")
    print(f"  Min rating: {preferences.min_rating}")
    print(f"{'='*60}")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Score: {result['score']:.3f}")
        print(f"   Genres: {', '.join(result['genres'])}")
        print(f"   Rating: {result['rating']}")
