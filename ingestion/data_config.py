"""
Data Configuration Module
Maps your dataset columns to the required Movie model fields.
This makes the system work with ANY movie dataset!
"""
from typing import Dict, List, Optional, Callable
import pandas as pd


class DataConfig:
    """
    Configuration for mapping your dataset columns to Movie model fields.
    
    Example:
        # For TMDB dataset
        config = DataConfig(
            movie_id_col='id',
            title_col='title',
            genres_col='genres',
            overview_col='overview',
            language_col='original_language',
            rating_col='vote_average'
        )
    """
    
    def __init__(
        self,
        movie_id_col: str = 'movie_id',
        title_col: str = 'title',
        genres_col: str = 'genres',
        overview_col: str = 'overview',
        language_col: str = 'language',
        rating_col: str = 'rating',
        release_date_col: Optional[str] = 'release_date',
        # Optional columns
        popularity_col: Optional[str] = None,
        vote_count_col: Optional[str] = None,
        runtime_col: Optional[str] = None,
        # Custom parsers
        genre_parser: Optional[Callable] = None,
        rating_normalizer: Optional[Callable] = None
    ):
        """
        Initialize data configuration.
        
        Args:
            movie_id_col: Column name for movie ID
            title_col: Column name for movie title
            genres_col: Column name for genres
            overview_col: Column name for plot/overview
            language_col: Column name for language
            rating_col: Column name for rating
            release_date_col: Column name for release date (optional)
            popularity_col: Column name for popularity score (optional)
            vote_count_col: Column name for vote count (optional)
            runtime_col: Column name for runtime (optional)
            genre_parser: Custom function to parse genres
            rating_normalizer: Custom function to normalize ratings to 0-10 scale
        """
        # Required fields mapping
        self.column_mapping = {
            'movie_id': movie_id_col,
            'title': title_col,
            'genres': genres_col,
            'overview': overview_col,
            'language': language_col,
            'rating': rating_col
        }
        
        # Optional fields
        self.optional_mapping = {
            'release_date': release_date_col,
            'popularity': popularity_col,
            'vote_count': vote_count_col,
            'runtime': runtime_col
        }
        
        # Custom parsers
        self.genre_parser = genre_parser or self._default_genre_parser
        self.rating_normalizer = rating_normalizer or self._default_rating_normalizer
    
    def _default_genre_parser(self, genre_string: str) -> List[str]:
        """
        Default genre parser for comma-separated strings.
        Override this for JSON or other formats.
        """
        if pd.isna(genre_string) or not genre_string:
            return ['Unknown']
        
        # Handle JSON format: [{"name": "Action"}, {"name": "Drama"}]
        if genre_string.startswith('['):
            import json
            try:
                genre_list = json.loads(genre_string)
                if isinstance(genre_list, list) and len(genre_list) > 0:
                    if isinstance(genre_list[0], dict):
                        return [g.get('name', '') for g in genre_list if g.get('name')]
            except:
                pass
        
        # Handle simple comma-separated: "Action, Drama, Thriller"
        genres = [g.strip() for g in str(genre_string).split(',')]
        return [g for g in genres if g] or ['Unknown']
    
    def _default_rating_normalizer(self, rating: float) -> float:
        """
        Default rating normalizer.
        Assumes ratings are already on 0-10 scale.
        Override for different scales (e.g., 0-5 stars).
        """
        try:
            rating = float(rating)
            # Clamp to 0-10
            return max(0.0, min(10.0, rating))
        except:
            return 0.0
    
    def get_required_columns(self) -> List[str]:
        """Get list of required column names in the dataset."""
        return list(self.column_mapping.values())
    
    def map_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map dataset columns to standard Movie model columns.
        
        Args:
            df: Raw DataFrame with dataset-specific columns
            
        Returns:
            DataFrame with standardized column names
        """
        # Create mapped DataFrame
        mapped_df = pd.DataFrame()
        
        # Map required columns
        for standard_name, dataset_column in self.column_mapping.items():
            if dataset_column not in df.columns:
                raise ValueError(f"Required column '{dataset_column}' not found in dataset!")
            mapped_df[standard_name] = df[dataset_column]
        
        # Map optional columns
        for standard_name, dataset_column in self.optional_mapping.items():
            if dataset_column and dataset_column in df.columns:
                mapped_df[standard_name] = df[dataset_column]
        
        return mapped_df


# ============================================================================
# PRE-CONFIGURED PROFILES FOR POPULAR DATASETS
# ============================================================================

class TMDBConfig(DataConfig):
    """Configuration for TMDB (The Movie Database) format."""
    
    def __init__(self):
        super().__init__(
            movie_id_col='id',
            title_col='title',
            genres_col='genres',
            overview_col='overview',
            language_col='original_language',
            rating_col='vote_average',
            release_date_col='release_date',
            popularity_col='popularity',
            vote_count_col='vote_count',
            runtime_col='runtime'
        )


class IMDBConfig(DataConfig):
    """Configuration for IMDB format."""
    
    def __init__(self):
        super().__init__(
            movie_id_col='imdb_id',
            title_col='title',
            genres_col='genres',
            overview_col='plot',
            language_col='language',
            rating_col='imdb_rating',
            release_date_col='year'
        )


class MovieLensConfig(DataConfig):
    """Configuration for MovieLens format."""
    
    def __init__(self):
        super().__init__(
            movie_id_col='movieId',
            title_col='title',
            genres_col='genres',
            overview_col='description',
            language_col='language',
            rating_col='rating'
        )
    
    def _default_genre_parser(self, genre_string: str) -> List[str]:
        """MovieLens uses pipe-separated genres."""
        if pd.isna(genre_string) or not genre_string:
            return ['Unknown']
        return [g.strip() for g in str(genre_string).split('|') if g.strip()]


# ============================================================================
# AUTO-DETECTION
# ============================================================================

def auto_detect_config(df: pd.DataFrame) -> DataConfig:
    """
    Automatically detect the best configuration for a dataset.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        DataConfig instance
    """
    columns = set(df.columns)
    
    # Check for TMDB format
    if {'id', 'title', 'genres', 'overview', 'vote_average'}.issubset(columns):
        print("✓ Detected TMDB format")
        return TMDBConfig()
    
    # Check for IMDB format
    if {'imdb_id', 'title', 'plot', 'imdb_rating'}.issubset(columns):
        print("✓ Detected IMDB format")
        return IMDBConfig()
    
    # Check for MovieLens format
    if {'movieId', 'title', 'genres'}.issubset(columns):
        print("✓ Detected MovieLens format")
        return MovieLensConfig()
    
    # Default: try to infer
    print("⚠ Could not auto-detect format, attempting to infer...")
    
    config_kwargs = {}
    
    # Infer movie_id column
    for col in ['id', 'movie_id', 'movieId', 'imdb_id', 'tmdb_id']:
        if col in columns:
            config_kwargs['movie_id_col'] = col
            break
    
    # Infer title column
    for col in ['title', 'movie_title', 'name']:
        if col in columns:
            config_kwargs['title_col'] = col
            break
    
    # Infer genres column
    for col in ['genres', 'genre', 'categories']:
        if col in columns:
            config_kwargs['genres_col'] = col
            break
    
    # Infer overview column
    for col in ['overview', 'description', 'plot', 'summary', 'synopsis']:
        if col in columns:
            config_kwargs['overview_col'] = col
            break
    
    # Infer language column
    for col in ['language', 'original_language', 'lang', 'spoken_languages']:
        if col in columns:
            config_kwargs['language_col'] = col
            break
    
    # Infer rating column
    for col in ['rating', 'vote_average', 'imdb_rating', 'score', 'user_rating']:
        if col in columns:
            config_kwargs['rating_col'] = col
            break
    
    if len(config_kwargs) < 6:
        raise ValueError(
            f"Could not auto-detect all required columns. Found: {config_kwargs}\n"
            "Please create a custom DataConfig manually."
        )
    
    print(f"✓ Inferred configuration: {config_kwargs}")
    return DataConfig(**config_kwargs)


if __name__ == "__main__":
    # Example usage
    print("Available pre-configured formats:")
    print("  - TMDBConfig() for TMDB datasets")
    print("  - IMDBConfig() for IMDB datasets")
    print("  - MovieLensConfig() for MovieLens datasets")
    print("\nOr create custom config:")
    print("  config = DataConfig(movie_id_col='your_id_col', ...)")
