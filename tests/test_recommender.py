"""
Unit tests for the Movie Recommendation System
Run with: pytest tests/
"""
import pytest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.movie import Movie
from ingestion.loader import MovieDataLoader
from features.feature_builder import FeatureBuilder
from similarity.similarity_engine import SimilarityEngine
from preferences.preference_engine import PreferenceEngine, UserPreferences


class TestMovieModel:
    """Test the Movie data model."""
    
    def test_movie_creation(self):
        """Test basic movie creation."""
        movie = Movie(
            movie_id=1,
            title="Test Movie",
            genres=["Action", "Drama"],
            overview="A test movie",
            language="en",
            rating=8.5
        )
        
        assert movie.movie_id == 1
        assert movie.title == "Test Movie"
        assert len(movie.genres) == 2
        assert movie.rating == 8.5
    
    def test_genre_parsing(self):
        """Test genre string parsing."""
        movie = Movie(
            movie_id=1,
            title="Test",
            genres="Action, Drama, Sci-Fi",
            overview="Test",
            language="en",
            rating=7.0
        )
        
        assert len(movie.genres) == 3
        assert "Action" in movie.genres
    
    def test_rating_validation(self):
        """Test rating bounds."""
        movie = Movie(
            movie_id=1,
            title="Test",
            genres=["Drama"],
            overview="Test",
            language="en",
            rating=15.0  # Invalid
        )
        
        assert movie.rating == 0.0  # Should be normalized


class TestDataIngestion:
    """Test data loading and validation."""
    
    @pytest.fixture
    def sample_csv_path(self, tmp_path):
        """Create a temporary CSV file."""
        csv_path = tmp_path / "test_movies.csv"
        csv_content = """movie_id,title,genres,overview,language,rating
1,Movie A,"Action, Drama",Overview A,en,8.5
2,Movie B,Comedy,Overview B,en,7.2
"""
        csv_path.write_text(csv_content)
        return str(csv_path)
    
    def test_loader_basic(self, sample_csv_path):
        """Test basic data loading."""
        loader = MovieDataLoader(sample_csv_path)
        movies = loader.load()
        
        assert len(movies) == 2
        assert all(isinstance(m, Movie) for m in movies)
    
    def test_schema_validation(self, tmp_path):
        """Test schema validation with missing columns."""
        csv_path = tmp_path / "invalid.csv"
        csv_path.write_text("movie_id,title\n1,Movie A\n")
        
        loader = MovieDataLoader(str(csv_path))
        
        with pytest.raises(ValueError, match="Missing required columns"):
            loader.load()


class TestFeatureBuilder:
    """Test feature engineering."""
    
    @pytest.fixture
    def sample_movies(self):
        """Create sample movies."""
        return [
            Movie(1, "Movie A", ["Action"], "Action packed movie", "en", 8.0),
            Movie(2, "Movie B", ["Drama"], "Dramatic story", "en", 7.5),
            Movie(3, "Movie C", ["Action", "Sci-Fi"], "Sci-fi action", "en", 8.5),
        ]
    
    def test_feature_matrix_shape(self, sample_movies):
        """Test feature matrix dimensions."""
        builder = FeatureBuilder(max_features=100)
        features = builder.build_features(sample_movies)
        
        assert features.shape[0] == len(sample_movies)
        assert features.shape[1] > 0
    
    def test_index_mapping(self, sample_movies):
        """Test movie ID to index mapping."""
        builder = FeatureBuilder()
        builder.build_features(sample_movies)
        
        assert builder.get_movie_index(1) == 0
        assert builder.get_movie_id(0) == 1


class TestSimilarityEngine:
    """Test similarity computation."""
    
    def test_similarity_computation(self):
        """Test basic similarity computation."""
        # Create simple feature matrix
        features = np.array([
            [1, 0, 0],
            [0.9, 0.1, 0],
            [0, 1, 0]
        ])
        
        engine = SimilarityEngine(features)
        similar = engine.find_similar_items(0, top_k=2)
        
        assert len(similar) == 2
        # Most similar to [1,0,0] should be [0.9,0.1,0]
        assert similar[0][0] == 1


class TestPreferenceEngine:
    """Test preference application."""
    
    @pytest.fixture
    def sample_movies(self):
        return [
            Movie(1, "Action Movie", ["Action"], "Overview", "en", 8.0),
            Movie(2, "Drama Movie", ["Drama"], "Overview", "en", 7.0),
            Movie(3, "Action Drama", ["Action", "Drama"], "Overview", "en", 9.0),
        ]
    
    def test_genre_boost(self, sample_movies):
        """Test genre preference boost."""
        engine = PreferenceEngine(sample_movies)
        prefs = UserPreferences(preferred_genres=["Action"])
        
        candidates = [(1, 1.0), (2, 1.0), (3, 1.0)]
        results = engine.apply_preferences(candidates, prefs)
        
        # Movies with Action genre should be boosted
        action_scores = [s for mid, s in results if mid in [1, 3]]
        drama_scores = [s for mid, s in results if mid == 2]
        
        assert all(a > d for a in action_scores for d in drama_scores)


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_pipeline(self, tmp_path):
        """Test complete recommendation pipeline."""
        # Create test data
        csv_path = tmp_path / "movies.csv"
        csv_content = """movie_id,title,genres,overview,language,rating
1,Matrix,"Action, Sci-Fi",Sci-fi action movie,en,8.7
2,Inception,"Action, Sci-Fi",Dream heist movie,en,8.8
3,Notebook,Romance,Romantic drama,en,7.8
"""
        csv_path.write_text(csv_content)
        
        # Load data
        loader = MovieDataLoader(str(csv_path))
        movies = loader.load()
        
        # Build features
        builder = FeatureBuilder()
        features = builder.build_features(movies)
        
        # Compute similarity
        engine = SimilarityEngine(features)
        similar = engine.find_similar_items(0, top_k=2)
        
        # Should find Inception as most similar to Matrix
        candidates = [(builder.get_movie_id(idx), score) for idx, score in similar]
        assert candidates[0][0] == 2  # Inception


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
