"""
Data Ingestion Module - PRIMARY IDENTITY
Responsibilities:
- Load raw CSV data
- Validate schema
- Clean and preprocess
- Convert to canonical Movie objects

NO ML logic here. Pure data engineering.
"""
import pandas as pd
from typing import List, Optional
import logging
from pathlib import Path

from models.movie import Movie
from ingestion.data_config import DataConfig, auto_detect_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MovieDataLoader:
    """
    Loads and validates movie data from CSV files.
    Converts raw data into canonical Movie objects.
    Now supports ANY dataset format via DataConfig!
    """

    def __init__(self, data_path: str, config: Optional[DataConfig] = None):
        """
        Initialize the data loader.

        Args:
            data_path: Path to the CSV file containing movie data
            config: DataConfig instance for column mapping (auto-detects if None)
        """
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        self.config = config  # Will be set during load if None

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate that all required columns exist based on config.
        Fail fast with clear error messages.

        Args:
            df: Raw DataFrame loaded from CSV

        Raises:
            ValueError: If required columns are missing
        """
        required_cols = self.config.get_required_columns()
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}\n"
                f"Available columns: {list(df.columns)[:20]}...\n"
                f"If your dataset has different column names, create a DataConfig."
            )
        logger.info("✓ Schema validation passed")

    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize the raw DataFrame.
        Deterministic preprocessing rules.

        Args:
            df: Raw DataFrame (with original column names)

        Returns:
            Cleaned DataFrame (with standardized column names)
        """
        df = df.copy()

        # Map columns to standard names
        df = self.config.map_dataframe(df)

        # Handle missing values (now using standardized column names)
        df['overview'] = df['overview'].fillna('No description available')
        df['title'] = df['title'].fillna('Unknown Title')
        df['genres'] = df['genres'].fillna('Unknown')
        df['language'] = df['language'].fillna('unknown')
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)

        # Ensure movie_id is integer
        df['movie_id'] = pd.to_numeric(df['movie_id'], errors='coerce').fillna(0).astype(int)

        # Remove duplicates based on movie_id
        df = df.drop_duplicates(subset=['movie_id'], keep='first')

        # Remove rows with invalid IDs
        df = df[df['movie_id'] > 0]

        logger.info(f"✓ Preprocessed {len(df)} movies")
        return df

    def _parse_genres(self, genre_string: str) -> List[str]:
        """
        Parse genre string using config's custom parser.

        Args:
            genre_string: Genre string in dataset format

        Returns:
            List of genre names
        """
        return self.config.genre_parser(genre_string)

    def _normalize_rating(self, rating: float) -> float:
        """
        Normalize rating using config's normalizer.

        Args:
            rating: Raw rating value

        Returns:
            Normalized rating (0-10 scale)
        """
        return self.config.rating_normalizer(rating)

    def _create_movie_object(self, row: pd.Series) -> Movie:
        """
        Convert a DataFrame row to a Movie object.

        Args:
            row: Single row from DataFrame (with standardized column names)

        Returns:
            Movie object
        """
        # Extract release year if available
        metadata = {}
        if 'release_date' in row and pd.notna(row['release_date']):
            try:
                year = pd.to_datetime(row['release_date']).year
                metadata['release_year'] = year
            except:
                pass

        # Add any extra metadata from optional columns
        for col in ['popularity', 'vote_count', 'runtime']:
            if col in row.index and pd.notna(row[col]):
                metadata[col] = row[col]

        # Parse genres using config
        genres = self._parse_genres(row['genres'])

        # Normalize rating using config
        rating = self._normalize_rating(row['rating'])

        return Movie(
            movie_id=int(row['movie_id']),
            title=str(row['title']),
            genres=genres,
            overview=str(row['overview']),
            language=str(row['language']),
            rating=rating,
            metadata=metadata
        )

    def load(self) -> List[Movie]:
        """
        Load and process the movie dataset.

        Returns:
            List of Movie objects
        """
        logger.info(f"Loading data from {self.data_path}")

        # Load CSV
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(df)} raw records")

        # Auto-detect config if not provided
        if self.config is None:
            logger.info("No config provided, attempting auto-detection...")
            self.config = auto_detect_config(df)

        # Validate schema (before mapping)
        self._validate_schema(df)

        # Preprocess (includes column mapping)
        df = self._preprocess_dataframe(df)
        
        # Convert to Movie objects
        movies = []
        for _, row in df.iterrows():
            try:
                movie = self._create_movie_object(row)
                movies.append(movie)
            except Exception as e:
                logger.warning(f"Failed to create movie from row: {e}")
                continue
        
        logger.info(f"✓ Successfully created {len(movies)} Movie objects")
        return movies


def create_sample_dataset(output_path: str = 'data/movies.csv') -> None:
    """
    Create a sample movie dataset for testing.
    
    Args:
        output_path: Where to save the sample CSV
    """
    sample_data = {
        'movie_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'title': [
            'The Matrix',
            'Inception',
            'Interstellar',
            'The Dark Knight',
            'Pulp Fiction',
            'Forrest Gump',
            'The Shawshank Redemption',
            'The Godfather',
            'Schindler\'s List',
            'Fight Club'
        ],
        'genres': [
            'Action, Sci-Fi',
            'Action, Sci-Fi, Thriller',
            'Sci-Fi, Drama, Adventure',
            'Action, Crime, Drama',
            'Crime, Drama',
            'Drama, Romance',
            'Drama',
            'Crime, Drama',
            'Biography, Drama, History',
            'Drama'
        ],
        'overview': [
            'A computer hacker learns about the true nature of reality and his role in the war against its controllers.',
            'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.',
            'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest tests.',
            'The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine in four tales of violence.',
            'The presidencies of Kennedy and Johnson unfold through the perspective of an Alabama man.',
            'Two imprisoned men bond over a number of years, finding solace and eventual redemption.',
            'The aging patriarch of an organized crime dynasty transfers control to his reluctant son.',
            'In German-occupied Poland, industrialist Oskar Schindler saves his Jewish employees from the Holocaust.',
            'An insomniac office worker and a soap salesman build an underground fight club.'
        ],
        'language': ['en', 'en', 'en', 'en', 'en', 'en', 'en', 'en', 'en', 'en'],
        'rating': [8.7, 8.8, 8.6, 9.0, 8.9, 8.8, 9.3, 9.2, 9.0, 8.8],
        'release_date': [
            '1999-03-31', '2010-07-16', '2014-11-07', '2008-07-18', '1994-10-14',
            '1994-07-06', '1994-09-23', '1972-03-24', '1993-12-15', '1999-10-15'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"✓ Sample dataset created at {output_path}")


if __name__ == "__main__":
    # Example usage
    create_sample_dataset()
    loader = MovieDataLoader('data/movies.csv')
    movies = loader.load()
    
    print(f"\n{'='*60}")
    print(f"Loaded {len(movies)} movies")
    print(f"{'='*60}")
    print(f"\nSample movie:")
    print(movies[0])
    print(f"\nMovie details:")
    print(f"  Title: {movies[0].title}")
    print(f"  Genres: {', '.join(movies[0].genres)}")
    print(f"  Rating: {movies[0].rating}")
    print(f"  Overview: {movies[0].overview[:100]}...")
