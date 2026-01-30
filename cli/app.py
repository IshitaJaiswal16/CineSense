"""
CLI Interface for Movie Recommendation System
Simple command-line interface for getting recommendations.
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import MovieRecommender
from preferences.preference_engine import UserPreferences


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*70)
    print(" "*15 + "🎬 MOVIE RECOMMENDATION SYSTEM 🎬")
    print("="*70 + "\n")


def print_recommendations(recommendations, query_title):
    """Pretty print recommendations."""
    if not recommendations:
        print(f"\n❌ No recommendations found for '{query_title}'")
        return
    
    print(f"\n{'='*70}")
    print(f"🎥 Recommendations for: {query_title}")
    print(f"{'='*70}\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   {'─' * 60}")
        print(f"   Score: {rec['score']:.3f} | Rating: {rec['rating']}/10")
        print(f"   Genres: {', '.join(rec['genres'])}")
        print(f"   {rec['overview'][:100]}...")
        print()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Get movie recommendations from the command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic recommendation
  python cli/app.py --movie "The Matrix"
  
  # With genre preferences
  python cli/app.py --movie "Inception" --genres "Sci-Fi,Action" --top 5
  
  # With minimum rating filter
  python cli/app.py --movie "The Matrix" --min-rating 8.0 --top 3
        """
    )
    
    parser.add_argument(
        '--movie',
        type=str,
        required=True,
        help='Movie title to get recommendations for'
    )
    
    parser.add_argument(
        '--genres',
        type=str,
        help='Comma-separated list of preferred genres'
    )
    
    parser.add_argument(
        '--languages',
        type=str,
        help='Comma-separated list of preferred language codes'
    )
    
    parser.add_argument(
        '--min-rating',
        type=float,
        default=0.0,
        help='Minimum rating filter (0-10)'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=5,
        help='Number of recommendations to show'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        default='data/movies.csv',
        help='Path to movie data CSV file'
    )
    
    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Rebuild feature cache'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Initialize recommender
    print("🔄 Initializing recommendation system...\n")
    try:
        recommender = MovieRecommender(
            data_path=args.data,
            rebuild_features=args.rebuild
        )
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: Create sample data with:")
        print("   python -c 'from ingestion.loader import create_sample_dataset; create_sample_dataset()'")
        return
    
    # Build preferences
    preferences = None
    if args.genres or args.languages or args.min_rating > 0:
        preferred_genres = [g.strip() for g in args.genres.split(',')] if args.genres else []
        preferred_languages = [l.strip() for l in args.languages.split(',')] if args.languages else []
        
        preferences = UserPreferences(
            preferred_genres=preferred_genres,
            preferred_languages=preferred_languages,
            min_rating=args.min_rating
        )
        
        print(f"✓ Preferences applied:")
        if preferred_genres:
            print(f"  • Genres: {', '.join(preferred_genres)}")
        if preferred_languages:
            print(f"  • Languages: {', '.join(preferred_languages)}")
        if args.min_rating > 0:
            print(f"  • Min Rating: {args.min_rating}")
        print()
    
    # Get recommendations
    recommendations = recommender.get_recommendations(
        movie_title=args.movie,
        preferences=preferences,
        top_k=args.top
    )
    
    # Display results
    print_recommendations(recommendations, args.movie)
    
    # Show dataset info
    print(f"{'='*70}")
    print(f"📊 Dataset: {len(recommender.movies)} movies")
    print(f"🎭 Genres: {', '.join(recommender.get_available_genres())}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
