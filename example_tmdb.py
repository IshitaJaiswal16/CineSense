"""
Example: Using the System with TMDB Dataset (4800+ movies)

This script demonstrates how to use the uploaded movies.csv dataset
which contains 4803 movies in TMDB format.
"""

from main import MovieRecommender
from ingestion.data_config import TMDBConfig
from preferences.preference_engine import UserPreferences


def main():
    """Run recommendation examples with the large TMDB dataset."""
    
    print("=" * 70)
    print(" " * 15 + "🎬 TMDB MOVIE RECOMMENDER 🎬")
    print("=" * 70)
    print()
    
    # Initialize with TMDB configuration
    print("Loading TMDB dataset (4800+ movies)...")
    recommender = MovieRecommender(
        data_path='data/movies.csv',  # Your uploaded dataset
        config=TMDBConfig(),     # Use TMDB format
        rebuild_features=True    # Build features from scratch
    )
    
    print(f"\n✓ Loaded {len(recommender.movies)} movies!")
    print(f"✓ Available genres: {', '.join(recommender.get_available_genres()[:10])}...")
    
    # Example 1: Basic recommendations
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Movies Similar to Avatar")
    print("=" * 70)
    
    results = recommender.get_recommendations("Avatar", top_k=5)
    
    for i, rec in enumerate(results, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Score: {rec['score']:.3f} | Rating: {rec['rating']}/10")
        print(f"   Genres: {', '.join(rec['genres'][:3])}...")  # Show first 3 genres
        print(f"   {rec['overview'][:100]}...")
    
    # Example 2: With preferences
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Action Movies Similar to Avatar (Rating > 7.0)")
    print("=" * 70)
    
    prefs = UserPreferences(
        preferred_genres=['Action', 'Adventure', 'Science Fiction'],
        min_rating=7.0,
        genre_weight=0.4
    )
    
    results = recommender.get_recommendations(
        "Avatar",
        preferences=prefs,
        top_k=5
    )
    
    for i, rec in enumerate(results, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Score: {rec['score']:.3f} | Rating: {rec['rating']}/10")
        print(f"   Genres: {', '.join(rec['genres'][:3])}...")
    
    # Example 3: Different movie
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Movies Similar to The Dark Knight")
    print("=" * 70)
    
    results = recommender.get_recommendations("The Dark Knight", top_k=5)
    
    for i, rec in enumerate(results, 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Score: {rec['score']:.3f} | Rating: {rec['rating']}/10")
        print(f"   Genres: {', '.join(rec['genres'][:3])}...")
    
    # Show some dataset statistics
    print("\n" + "=" * 70)
    print("DATASET STATISTICS")
    print("=" * 70)
    print(f"\nTotal Movies: {len(recommender.movies)}")
    print(f"Total Genres: {len(recommender.get_available_genres())}")
    print(f"Languages: {len(recommender.get_available_languages())}")
    
    # Top rated movies
    sorted_movies = sorted(recommender.movies, key=lambda m: m.rating, reverse=True)
    print(f"\nTop 5 Rated Movies:")
    for i, movie in enumerate(sorted_movies[:5], 1):
        print(f"  {i}. {movie.title} - {movie.rating}/10")
    
    print("\n" + "=" * 70)
    print("🎉 All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
