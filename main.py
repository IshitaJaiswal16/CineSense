"""
Main Recommendation Pipeline - ORCHESTRATION LAYER
Responsibilities:
- Connect all components
- Coordinate the recommendation flow
- NO business logic here, only workflow

This is the entry point for the recommendation system.
"""
import logging
from typing import List, Dict, Optional
from pathlib import Path

from models.movie import Movie
from ingestion.loader import MovieDataLoader
from features.feature_builder import FeatureBuilder
from similarity.similarity_engine import SimilarityEngine
from preferences.preference_engine import PreferenceEngine, UserPreferences

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MovieRecommender:
    """
    Main recommendation pipeline orchestrator.
    Coordinates data loading, feature building, and recommendation generation.
    """
    
    def __init__(
        self,
        data_path: str,
        cache_dir: str = 'cache',
        rebuild_features: bool = False
    ):
        """
        Initialize the recommendation system.
        
        Args:
            data_path: Path to movie data CSV
            cache_dir: Directory for caching features
            rebuild_features: Whether to rebuild features from scratch
        """
        self.data_path = data_path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.movies: List[Movie] = []
        self.feature_builder: Optional[FeatureBuilder] = None
        self.similarity_engine: Optional[SimilarityEngine] = None
        self.preference_engine: Optional[PreferenceEngine] = None
        
        # Initialize
        self._initialize(rebuild_features)
    
    def _initialize(self, rebuild: bool) -> None:
        """
        Initialize all pipeline components.
        
        Args:
            rebuild: Whether to rebuild cached features
        """
        logger.info("="*60)
        logger.info("Initializing Movie Recommendation System")
        logger.info("="*60)
        
        # Step 1: Load data
        logger.info("\n[1/4] Loading movie data...")
        loader = MovieDataLoader(self.data_path)
        self.movies = loader.load()
        
        # Step 2: Build features
        logger.info("\n[2/4] Building features...")
        self.feature_builder = FeatureBuilder()
        
        cache_exists = (self.cache_dir / 'mappings.pkl').exists()
        
        if not rebuild and cache_exists:
            logger.info("Loading cached features...")
            self.feature_builder.load(str(self.cache_dir))
            # Still need to rebuild the actual matrix
            feature_matrix = self.feature_builder.build_features(self.movies)
        else:
            logger.info("Building features from scratch...")
            feature_matrix = self.feature_builder.build_features(self.movies)
            self.feature_builder.save(str(self.cache_dir))
        
        # Step 3: Initialize similarity engine
        logger.info("\n[3/4] Initializing similarity engine...")
        self.similarity_engine = SimilarityEngine(feature_matrix)
        
        # Step 4: Initialize preference engine
        logger.info("\n[4/4] Initializing preference engine...")
        self.preference_engine = PreferenceEngine(self.movies)
        
        logger.info("\n" + "="*60)
        logger.info("✓ System initialized successfully!")
        logger.info("="*60 + "\n")
    
    def find_movie_by_title(self, title: str, fuzzy: bool = True) -> Optional[Movie]:
        """
        Find a movie by title.
        
        Args:
            title: Movie title to search for
            fuzzy: Whether to use fuzzy matching
            
        Returns:
            Movie object if found, None otherwise
        """
        title_lower = title.lower()
        
        # Exact match first
        for movie in self.movies:
            if movie.title.lower() == title_lower:
                return movie
        
        # Fuzzy match
        if fuzzy:
            for movie in self.movies:
                if title_lower in movie.title.lower():
                    return movie
        
        return None
    
    def get_recommendations(
        self,
        movie_title: str,
        preferences: Optional[UserPreferences] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Get movie recommendations for a given movie.
        
        Args:
            movie_title: Title of the movie to base recommendations on
            preferences: Optional user preferences for personalization
            top_k: Number of recommendations to return
            
        Returns:
            List of recommendation dicts with movie info and scores
        """
        # Find the query movie
        query_movie = self.find_movie_by_title(movie_title)
        if not query_movie:
            logger.error(f"Movie '{movie_title}' not found")
            return []
        
        logger.info(f"\nGenerating recommendations for: {query_movie.title}")
        
        # Get movie index
        try:
            query_idx = self.feature_builder.get_movie_index(query_movie.movie_id)
        except KeyError:
            logger.error(f"Movie ID {query_movie.movie_id} not in feature index")
            return []
        
        # Find similar movies
        similar_indices = self.similarity_engine.find_similar_items(
            query_idx,
            top_k=top_k * 2  # Get more candidates for preference filtering
        )
        
        # Convert to movie IDs
        candidates = [
            (self.feature_builder.get_movie_id(idx), score)
            for idx, score in similar_indices
        ]
        
        # Apply preferences if provided
        if preferences:
            logger.info(f"Applying preferences: {preferences}")
            results = self.preference_engine.filter_and_rank(
                candidates,
                preferences,
                top_k=top_k
            )
        else:
            # No preferences - just return top candidates
            results = []
            for movie_id, score in candidates[:top_k]:
                movie = next(m for m in self.movies if m.movie_id == movie_id)
                results.append({
                    'movie_id': movie_id,
                    'title': movie.title,
                    'genres': movie.genres,
                    'language': movie.language,
                    'rating': movie.rating,
                    'overview': movie.overview,
                    'score': score,
                    'metadata': movie.metadata
                })
        
        return results
    
    def get_recommendations_by_id(
        self,
        movie_id: int,
        preferences: Optional[UserPreferences] = None,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Get recommendations by movie ID.
        
        Args:
            movie_id: ID of the movie
            preferences: Optional user preferences
            top_k: Number of recommendations
            
        Returns:
            List of recommendations
        """
        movie = next((m for m in self.movies if m.movie_id == movie_id), None)
        if not movie:
            logger.error(f"Movie ID {movie_id} not found")
            return []
        
        return self.get_recommendations(movie.title, preferences, top_k)
    
    def get_all_movies(self) -> List[Movie]:
        """Get all available movies."""
        return self.movies
    
    def get_available_genres(self) -> List[str]:
        """Get list of all unique genres in the dataset."""
        all_genres = set()
        for movie in self.movies:
            all_genres.update(movie.genres)
        return sorted(list(all_genres))
    
    def get_available_languages(self) -> List[str]:
        """Get list of all unique languages in the dataset."""
        return sorted(list(set(movie.language for movie in self.movies)))


def main():
    """Example usage of the recommendation system."""
    
    # Initialize system
    recommender = MovieRecommender(
        data_path='data/movies.csv',
        rebuild_features=True
    )
    
    # Example 1: Basic recommendations (no preferences)
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Recommendations")
    print("="*80)
    
    movie_title = "The Matrix"
    recommendations = recommender.get_recommendations(movie_title, top_k=5)
    
    print(f"\nTop 5 movies similar to '{movie_title}':\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Similarity Score: {rec['score']:.3f}")
        print(f"   Genres: {', '.join(rec['genres'])}")
        print(f"   Rating: {rec['rating']}/10")
        print()
    
    # Example 2: Personalized recommendations
    print("\n" + "="*80)
    print("EXAMPLE 2: Personalized Recommendations")
    print("="*80)
    
    user_prefs = UserPreferences(
        preferred_genres=['Sci-Fi', 'Action'],
        preferred_languages=['en'],
        genre_weight=0.4,
        language_weight=0.1,
        min_rating=7.5
    )
    
    print(f"\nUser Preferences:")
    print(f"  • Preferred Genres: {list(user_prefs.preferred_genres)}")
    print(f"  • Minimum Rating: {user_prefs.min_rating}")
    
    personalized = recommender.get_recommendations(
        movie_title,
        preferences=user_prefs,
        top_k=5
    )
    
    print(f"\nPersonalized recommendations for '{movie_title}':\n")
    for i, rec in enumerate(personalized, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Adjusted Score: {rec['score']:.3f}")
        print(f"   Genres: {', '.join(rec['genres'])}")
        print(f"   Rating: {rec['rating']}/10")
        print()
    
    # Show available data
    print("\n" + "="*80)
    print("DATASET INFO")
    print("="*80)
    print(f"\nTotal Movies: {len(recommender.movies)}")
    print(f"Available Genres: {', '.join(recommender.get_available_genres())}")
    print(f"Available Languages: {', '.join(recommender.get_available_languages())}")


if __name__ == "__main__":
    # First create sample data if it doesn't exist
    from ingestion.loader import create_sample_dataset
    
    if not Path('data/movies.csv').exists():
        print("Creating sample dataset...")
        create_sample_dataset()
    
    main()
