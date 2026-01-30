# 🎬 Movie Recommendation System

A production-ready, modular movie recommendation engine built with Python. Features content-based filtering with personalized user preferences, clean architecture, and multiple interfaces (CLI, Web UI).

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Key Features

- **Content-Based Filtering**: TF-IDF vectorization of movie overviews combined with genre and rating signals
- **Personalized Recommendations**: User preference engine with soft weighting (no hard filters)
- **Clean Architecture**: Modular design with clear separation of concerns
- **Multiple Interfaces**: CLI tool and Streamlit web application
- **Production-Ready**: Comprehensive logging, error handling, and caching
- **Type-Safe**: Full type hints and dataclass models
- **Extensible**: Easy to add new features or swap components

## 🏗️ Architecture

```
movie-recommendation-engine/
│
├── models/              # Data schemas (Movie dataclass)
├── ingestion/           # Data loading and validation
├── features/            # Feature engineering (TF-IDF, encoders)
├── similarity/          # Similarity computation (cosine similarity)
├── preferences/         # User preference handling
├── cli/                 # Command-line interface
├── app/                 # Streamlit web interface
├── main.py             # Main orchestrator
└── tests/              # Unit tests
```

### Component Responsibilities

| Component | Role | Key Principle |
|-----------|------|---------------|
| **Models** | Canonical data schema | All ML logic uses `Movie` objects |
| **Ingestion** | Data loading & validation | Fail fast with clear errors |
| **Features** | Feature engineering | Reproducible transformations |
| **Similarity** | Vector similarity | Domain-agnostic operations |
| **Preferences** | Personalization | Soft weighting, no hard filters |
| **Main** | Orchestration | No business logic, only coordination |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/movie-recommendation-engine.git
cd movie-recommendation-engine

# Install dependencies
pip install -r requirements.txt
```

### Generate Sample Data

```bash
python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"
```

### Run the System

**1. CLI Interface:**
```bash
python cli/app.py --movie "The Matrix" --top 5
```

**2. Web Interface:**
```bash
streamlit run app/streamlit_app.py
```

**3. Python API:**
```python
from main import MovieRecommender
from preferences.preference_engine import UserPreferences

# Initialize
recommender = MovieRecommender('data/movies.csv')

# Get recommendations
preferences = UserPreferences(
    preferred_genres=['Sci-Fi', 'Action'],
    min_rating=7.0
)

results = recommender.get_recommendations(
    movie_title="The Matrix",
    preferences=preferences,
    top_k=5
)

for rec in results:
    print(f"{rec['title']} - Score: {rec['score']:.3f}")
```

## 📊 How It Works

### 1. Data Ingestion
- Loads movie data from CSV
- Validates schema and handles missing values
- Converts to canonical `Movie` objects

### 2. Feature Engineering
- **Text Features**: TF-IDF vectorization of movie overviews
- **Categorical Features**: One-hot encoding of genres
- **Numerical Features**: Normalized ratings
- Creates bidirectional index mappings

### 3. Similarity Computation
- Computes cosine similarity between feature vectors
- Returns ranked candidates based on similarity scores

### 4. Preference Application (The Differentiator)
- Applies user preferences via soft weighting
- Boosts scores based on genre/language matches
- Applies penalties for low ratings (but doesn't filter)
- Re-ranks final results

## 💡 Usage Examples

### CLI Examples

```bash
# Basic recommendation
python cli/app.py --movie "Inception"

# With genre preferences
python cli/app.py --movie "The Matrix" --genres "Sci-Fi,Action" --top 3

# With minimum rating filter
python cli/app.py --movie "Pulp Fiction" --min-rating 8.5

# Full customization
python cli/app.py \
  --movie "Interstellar" \
  --genres "Sci-Fi,Drama" \
  --languages "en" \
  --min-rating 8.0 \
  --top 10
```

### Python API Examples

```python
from main import MovieRecommender
from preferences.preference_engine import UserPreferences

recommender = MovieRecommender('data/movies.csv')

# Example 1: Basic recommendations
recs = recommender.get_recommendations("The Godfather", top_k=5)

# Example 2: With preferences
prefs = UserPreferences(
    preferred_genres=['Crime', 'Drama'],
    genre_weight=0.4,
    min_rating=8.0
)
recs = recommender.get_recommendations("The Godfather", preferences=prefs)

# Example 3: Explore dataset
print(f"Total movies: {len(recommender.movies)}")
print(f"Genres: {recommender.get_available_genres()}")
```

## 🔧 Configuration

### Feature Builder Parameters

```python
FeatureBuilder(
    max_features=5000,      # Max TF-IDF features
    ngram_range=(1, 2),     # Unigrams and bigrams
    min_df=2                # Minimum document frequency
)
```

### User Preferences

```python
UserPreferences(
    preferred_genres=['Action', 'Sci-Fi'],  # Boost these genres
    preferred_languages=['en'],              # Boost these languages
    genre_weight=0.3,                        # Genre boost multiplier
    language_weight=0.2,                     # Language boost multiplier
    min_rating=7.0                           # Soft rating filter
)
```

## 📁 Data Format

The system expects a CSV file with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `movie_id` | int | Unique identifier |
| `title` | str | Movie title |
| `genres` | str | Comma-separated genres |
| `overview` | str | Plot description |
| `language` | str | Language code (e.g., 'en') |
| `rating` | float | Rating (0-10) |
| `release_date` | str | (Optional) Release date |

**Example:**
```csv
movie_id,title,genres,overview,language,rating,release_date
1,The Matrix,"Action, Sci-Fi","A computer hacker learns...",en,8.7,1999-03-31
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=.
```

## 🎯 Key Design Decisions

### 1. **Canonical Schema Pattern**
All downstream components work with `Movie` objects, not raw DataFrames. This ensures type safety and consistency.

### 2. **Layer Isolation**
- Ingestion layer: NO ML logic
- Feature layer: NO domain knowledge
- Similarity layer: Pure vector operations
- Preference layer: Business logic only

### 3. **Soft Preferences**
Instead of hard filtering (which removes items), we use soft weighting that boosts or penalizes scores. This prevents empty result sets and allows for better discovery.

### 4. **Reproducibility**
Feature builders can be saved and loaded, ensuring consistent results across runs.

## 🚧 Future Enhancements

- [ ] Collaborative filtering (user-user, item-item)
- [ ] Hybrid recommender (content + collaborative)
- [ ] Deep learning embeddings (BERT, USE)
- [ ] Real-time learning from user interactions
- [ ] A/B testing framework
- [ ] REST API with FastAPI
- [ ] Docker containerization
- [ ] Cloud deployment (AWS, GCP)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- Built following clean architecture principles
- Inspired by production recommender systems at scale
- Uses scikit-learn for ML operations

---

⭐ **Star this repo** if you find it helpful!
