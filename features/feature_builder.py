"""
Feature Engineering Module - SECONDARY IDENTITY
Responsibilities:
- Extract features from Movie objects
- Build feature matrices
- Maintain index mappings

This layer transforms canonical data into ML-ready representations.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from typing import List, Dict, Tuple
import logging
import pickle
from pathlib import Path

from models.movie import Movie

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureBuilder:
    """
    Builds feature representations from Movie objects.
    Combines text features (TF-IDF) with categorical signals.
    """
    
    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 1
    ):
        """
        Initialize the feature builder.
        
        Args:
            max_features: Maximum number of TF-IDF features
            ngram_range: Range of n-grams for TF-IDF
            min_df: Minimum document frequency for TF-IDF
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        
        # Vectorizers (fitted during build)
        self.tfidf_vectorizer = None
        self.genre_encoder = None
        
        # Index mappings
        self.movie_id_to_index: Dict[int, int] = {}
        self.index_to_movie_id: Dict[int, int] = {}
        
    def _build_text_features(self, movies: List[Movie]) -> np.ndarray:
        """
        Extract TF-IDF features from movie overviews.
        
        Args:
            movies: List of Movie objects
            
        Returns:
            TF-IDF feature matrix (n_movies, n_features)
        """
        logger.info("Building text features...")
        
        # Extract overviews
        overviews = [movie.overview for movie in movies]
        
        # Initialize and fit TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        
        # Transform to TF-IDF matrix
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(overviews)
        
        logger.info(f"✓ TF-IDF matrix shape: {tfidf_matrix.shape}")
        return tfidf_matrix.toarray()
    
    def _build_genre_features(self, movies: List[Movie]) -> np.ndarray:
        """
        Build one-hot encoded genre features.
        
        Args:
            movies: List of Movie objects
            
        Returns:
            Genre feature matrix (n_movies, n_genres)
        """
        logger.info("Building genre features...")
        
        # Extract genre lists
        genre_lists = [movie.genres for movie in movies]
        
        # Initialize and fit MultiLabelBinarizer
        self.genre_encoder = MultiLabelBinarizer()
        genre_matrix = self.genre_encoder.fit_transform(genre_lists)
        
        logger.info(f"✓ Genre matrix shape: {genre_matrix.shape}")
        logger.info(f"✓ Unique genres: {list(self.genre_encoder.classes_)}")
        return genre_matrix
    
    def _build_rating_features(self, movies: List[Movie]) -> np.ndarray:
        """
        Build rating-based features.
        
        Args:
            movies: List of Movie objects
            
        Returns:
            Rating feature matrix (n_movies, 1)
        """
        ratings = np.array([movie.rating for movie in movies]).reshape(-1, 1)
        
        # Normalize ratings to 0-1 scale
        ratings = ratings / 10.0
        
        return ratings
    
    def _create_index_mappings(self, movies: List[Movie]) -> None:
        """
        Create bidirectional mappings between movie IDs and matrix indices.
        
        Args:
            movies: List of Movie objects
        """
        self.movie_id_to_index = {
            movie.movie_id: idx for idx, movie in enumerate(movies)
        }
        self.index_to_movie_id = {
            idx: movie.movie_id for idx, movie in enumerate(movies)
        }
        logger.info(f"✓ Created index mappings for {len(movies)} movies")
    
    def build_features(
        self,
        movies: List[Movie],
        include_genres: bool = True,
        include_ratings: bool = True
    ) -> np.ndarray:
        """
        Build complete feature matrix from Movie objects.
        
        Args:
            movies: List of Movie objects
            include_genres: Whether to include genre features
            include_ratings: Whether to include rating features
            
        Returns:
            Combined feature matrix (n_movies, n_total_features)
        """
        logger.info(f"Building features for {len(movies)} movies...")
        
        # Create index mappings
        self._create_index_mappings(movies)
        
        # Build individual feature components
        text_features = self._build_text_features(movies)
        
        feature_components = [text_features]
        
        if include_genres:
            genre_features = self._build_genre_features(movies)
            feature_components.append(genre_features)
        
        if include_ratings:
            rating_features = self._build_rating_features(movies)
            feature_components.append(rating_features)
        
        # Concatenate all features
        feature_matrix = np.hstack(feature_components)
        
        logger.info(f"✓ Final feature matrix shape: {feature_matrix.shape}")
        return feature_matrix
    
    def get_movie_index(self, movie_id: int) -> int:
        """
        Get matrix index for a given movie ID.
        
        Args:
            movie_id: Movie ID to look up
            
        Returns:
            Matrix index
            
        Raises:
            KeyError: If movie ID not found
        """
        if movie_id not in self.movie_id_to_index:
            raise KeyError(f"Movie ID {movie_id} not found in index")
        return self.movie_id_to_index[movie_id]
    
    def get_movie_id(self, index: int) -> int:
        """
        Get movie ID for a given matrix index.
        
        Args:
            index: Matrix index
            
        Returns:
            Movie ID
        """
        return self.index_to_movie_id[index]
    
    def save(self, save_dir: str) -> None:
        """
        Save the feature builder state for reproducibility.
        
        Args:
            save_dir: Directory to save artifacts
        """
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save vectorizers
        with open(save_path / 'tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        with open(save_path / 'genre_encoder.pkl', 'wb') as f:
            pickle.dump(self.genre_encoder, f)
        
        # Save mappings
        with open(save_path / 'mappings.pkl', 'wb') as f:
            pickle.dump({
                'movie_id_to_index': self.movie_id_to_index,
                'index_to_movie_id': self.index_to_movie_id
            }, f)
        
        logger.info(f"✓ Feature builder saved to {save_dir}")
    
    def load(self, save_dir: str) -> None:
        """
        Load a previously saved feature builder state.
        
        Args:
            save_dir: Directory containing saved artifacts
        """
        save_path = Path(save_dir)
        
        # Load vectorizers
        with open(save_path / 'tfidf_vectorizer.pkl', 'rb') as f:
            self.tfidf_vectorizer = pickle.load(f)
        
        with open(save_path / 'genre_encoder.pkl', 'rb') as f:
            self.genre_encoder = pickle.load(f)
        
        # Load mappings
        with open(save_path / 'mappings.pkl', 'rb') as f:
            mappings = pickle.load(f)
            self.movie_id_to_index = mappings['movie_id_to_index']
            self.index_to_movie_id = mappings['index_to_movie_id']
        
        logger.info(f"✓ Feature builder loaded from {save_dir}")


if __name__ == "__main__":
    # Example usage
    from ingestion.loader import MovieDataLoader, create_sample_dataset
    
    # Create sample data and load
    create_sample_dataset()
    loader = MovieDataLoader('data/movies.csv')
    movies = loader.load()
    
    # Build features
    builder = FeatureBuilder()
    feature_matrix = builder.build_features(movies)
    
    print(f"\n{'='*60}")
    print(f"Feature Matrix Shape: {feature_matrix.shape}")
    print(f"{'='*60}")
    print(f"\nFeature breakdown:")
    print(f"  TF-IDF features: vocabulary size = {len(builder.tfidf_vectorizer.vocabulary_)}")
    print(f"  Genre features: {len(builder.genre_encoder.classes_)} genres")
    print(f"  Rating features: 1")
    
    # Test index mapping
    movie = movies[0]
    idx = builder.get_movie_index(movie.movie_id)
    print(f"\nIndex mapping test:")
    print(f"  Movie '{movie.title}' (ID: {movie.movie_id}) -> Index: {idx}")
