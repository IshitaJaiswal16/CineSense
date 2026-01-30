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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MovieDataLoader:
    """
    Loads and validates movie data from CSV files.
    Converts raw data into canonical Movie objects.
    """
    
    # Required columns for validation
    REQUIRED_COLUMNS = ['movie_id', 'title', 'genres', 'overview', 'language', 'rating']
    
    def __init__(self, data_path: str):
        """
        Initialize the data loader.
        
        Args:
            data_path: Path to the CSV file containing movie data
        """
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
    
    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate that all required columns exist.
        Fail fast with clear error messages.
        
        Args:
            df: Raw DataFrame loaded from CSV
            
        Raises:
            ValueError: If required columns are missing
        """
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}\n"
                f"Available columns: {list(df.columns)}"
            )
        logger.info("✓ Schema validation passed")
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize the raw DataFrame.
        Deterministic preprocessing rules.
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Handle missing values
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
        Parse genre string into a clean list.
        
        Args:
            genre_string: Comma-separated genre string
            
        Returns:
            List of genre names
        """
        if pd.isna(genre_string) or not genre_string:
            return ['Unknown']
        
        # Handle different formats
        genres = [g.strip() for g in str(genre_string).split(',')]
        return [g for g in genres if g]
    
    def _create_movie_object(self, row: pd.Series) -> Movie:
        """
        Convert a DataFrame row to a Movie object.
        
        Args:
            row: Single row from DataFrame
            
        Returns:
            Movie object
        """
        # Extract release year if available
        metadata = {}
        if 'release_date' in row:
            try:
                year = pd.to_datetime(row['release_date']).year
                metadata['release_year'] = year
            except:
                pass
        
        # Add any extra metadata
        for col in row.index:
            if col not in self.REQUIRED_COLUMNS and pd.notna(row[col]):
                metadata[col] = row[col]
        
        return Movie(
            movie_id=int(row['movie_id']),
            title=str(row['title']),
            genres=self._parse_genres(row['genres']),
            overview=str(row['overview']),
            language=str(row['language']),
            rating=float(row['rating']),
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
        
        # Validate schema
        self._validate_schema(df)
        
        # Preprocess
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
