"""
Streamlit Web Interface for Movie Recommendation System
Beautiful, interactive UI for getting personalized movie recommendations.
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import MovieRecommender
from preferences.preference_engine import UserPreferences


# Page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .movie-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .movie-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .movie-meta {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.2);
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_recommender(data_path='data/movies.csv'):
    """Load and cache the recommender system."""
    return MovieRecommender(data_path, rebuild_features=False)


def display_movie_card(movie_data, rank):
    """Display a movie as a card."""
    st.markdown(f"""
    <div class="movie-card">
        <div class="movie-title">#{rank} {movie_data['title']}</div>
        <div class="movie-meta">
            <span class="score-badge">Score: {movie_data['score']:.3f}</span>
            <span class="score-badge">⭐ {movie_data['rating']}/10</span>
        </div>
        <div class="movie-meta" style="margin-top: 0.5rem;">
            🎭 {', '.join(movie_data['genres'])} | 🗣️ {movie_data['language'].upper()}
        </div>
        <div style="margin-top: 1rem; font-size: 0.9rem;">
            {movie_data['overview'][:200]}...
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🎬 Movie Recommendation System")
    st.markdown("### Discover your next favorite movie!")
    
    # Initialize recommender
    try:
        recommender = load_recommender()
    except FileNotFoundError:
        st.error("❌ Movie data not found! Please run: `python -c 'from ingestion.loader import create_sample_dataset; create_sample_dataset()'`")
        return

    # Get all movie titles for search
    movie_titles = [m.title for m in recommender.get_all_movies()]

    # Main content area - Movie search
    st.markdown("---")

    # Search method selection
    search_method = st.radio(
        "Search Method:",
        ["Dropdown Selection", "Type to Search"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        if search_method == "Type to Search":
            # Text input search
            search_input = st.text_input(
                "🔍 Type movie name:",
                placeholder="e.g., The Matrix, Inception, Interstellar...",
                help="Start typing to search for a movie"
            )

            # Find matching movie
            if search_input:
                selected_movie = recommender.find_movie_by_title(search_input, fuzzy=True)
                if selected_movie:
                    st.success(f"✓ Found: **{selected_movie.title}**")
                    selected_movie = selected_movie.title
                else:
                    st.warning(f"❌ Movie '{search_input}' not found. Try a different name.")
                    selected_movie = None
            else:
                selected_movie = None
        else:
            # Dropdown selection
            selected_movie = st.selectbox(
                "🔍 Select a movie:",
                options=movie_titles,
                index=0,
                help="Choose from available movies"
            )

    with col2:
        # Number of recommendations
        top_k = st.number_input(
            "# Results:",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            help="Number of recommendations to show"
        )

    # Preferences in expandable section
    with st.expander("⚙️ Advanced Settings (Optional)", expanded=False):
        use_preferences = st.checkbox("Enable personalized preferences")

        preferences = None
        if use_preferences:
            col1, col2 = st.columns(2)

            with col1:
                # Genre preferences
                available_genres = recommender.get_available_genres()
                selected_genres = st.multiselect(
                    "Preferred Genres:",
                    options=available_genres,
                    default=[],
                    help="Boost movies with these genres"
                )

                # Minimum rating
                min_rating = st.slider(
                    "Minimum Rating:",
                    min_value=0.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.5,
                    help="Soft filter for movie ratings"
                )

            with col2:
                # Language preferences
                available_languages = recommender.get_available_languages()
                selected_languages = st.multiselect(
                    "Preferred Languages:",
                    options=available_languages,
                    default=[],
                    help="Boost movies in these languages"
                )

                # Weights
                genre_weight = st.slider(
                    "Genre importance:",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.3,
                    step=0.1,
                    help="How much to boost movies with preferred genres"
                )

            # Build preferences object
            if selected_genres or selected_languages or min_rating > 0:
                preferences = UserPreferences(
                    preferred_genres=selected_genres,
                    preferred_languages=selected_languages,
                    genre_weight=genre_weight,
                    language_weight=0.2,
                    min_rating=min_rating
                )

    st.markdown("---")

    # Get recommendations button (centered)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button(
            "🔍 Get Recommendations",
            type="primary",
            use_container_width=True,
            disabled=(selected_movie is None),
            key="search_recommendations"
        )

    # Process recommendations
    if search_button and selected_movie:
        with st.spinner("🎬 Finding perfect movies for you..."):
            recommendations = recommender.get_recommendations(
                movie_title=selected_movie,
                preferences=preferences,
                top_k=top_k
            )

        # Display results
        if recommendations:
            st.success(f"✓ Found {len(recommendations)} recommendations!")

            # Show query movie info
            query_movie = recommender.find_movie_by_title(selected_movie)
            if query_movie:
                st.markdown("### 📽️ Based on your selection:")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{query_movie.title}**")
                    st.caption(f"🎭 {', '.join(query_movie.genres)}")
                with col2:
                    st.metric("Rating", f"{query_movie.rating}/10")
                with col3:
                    st.metric("Language", query_movie.language.upper())

            # Display recommendations
            st.markdown("---")
            st.markdown("### 🎯 Your Recommendations:")

            for i, rec in enumerate(recommendations, 1):
                display_movie_card(rec, i)
        else:
            st.warning("❌ No recommendations found. Try adjusting your preferences.")
    else:
        # Welcome message when no search has been performed
        st.info("""
        👋 **Welcome to the Movie Recommendation System!**
        
        **How to use:**
        1. 🔍 **Search** for a movie (use dropdown OR type the name)
        2. 📊 **Choose** how many recommendations you want
        3. ⚙️ *(Optional)* Click "Advanced Settings" to personalize with your preferences
        4. 🎬 Click **"Get Recommendations"** to discover similar movies!
        
        💡 **Pro Tips:** 
        - Use "Type to Search" for faster movie lookup
        - Enable preferences and select your favorite genres for better recommendations
        - Try different movies to explore various recommendations
        """)

    # Footer with dataset info in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Dataset Info")
        st.info(f"""
        **Total Movies:** {len(recommender.movies)}  
        **Genres:** {len(recommender.get_available_genres())}  
        **Languages:** {len(recommender.get_available_languages())}
        """)

        st.markdown("---")
        st.markdown("### 🎭 Available Genres")
        st.caption(", ".join(recommender.get_available_genres()))

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("""
        This recommendation system uses **content-based filtering** 
        with TF-IDF vectorization and personalized preference weighting.
        
        **Built with:** Python, scikit-learn, Streamlit
        """)

        st.markdown("---")
        st.markdown("### 📚 Quick Examples")
        st.caption("""
        **Try these movies:**
        - The Matrix
        - Inception
        - The Godfather
        - Forrest Gump
        """)


if __name__ == "__main__":
    main()