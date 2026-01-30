# 🎬 CineSense

**AI-Powered Movie Preference & Ranking System**

CineSense is a **production-oriented movie recommendation system** designed to demonstrate
**end-to-end data engineering pipelines combined with applied machine learning**.

CineSense focuses on:
- **schema-flexible data ingestion**
- **clean modular architecture**
- **applied ML signals over real-world datasets**
- **multiple consumption layers (API, CLI, Web UI)**

It supports industry-standard datasets such as **TMDB, IMDB, MovieLens**, as well as **custom CSV formats**
through configurable schemas — making it adaptable, extensible, and production-ready.

---

## 🚀 Key Capabilities

- 🎯 **Content-Based Recommendation Engine**  
  TF-IDF–based semantic similarity with genre-aware feature enrichment


- 🧠 **Applied ML Personalization (Soft Constraints)**  
  User preferences influence ranking via weighted scoring — not hard filters


- 🏗️ **Data Engineering–First Design**  
  Canonical movie schema, validation, normalization, and format auto-detection


- 🔌 **Multi-Interface Access**  
  - Streamlit Web App  
  - Command-Line Interface (CLI)  
  - Python API for integration


- ⚡ **Performance-Oriented**  
  Feature caching and efficient similarity computation for sub-second results


- 🧩 **Clean, Extensible Architecture**  
  Modular layers built for testing, scalability, and future model upgrades
---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/IshitaJaiswal16/CineSense.git
cd CineSense

# Install dependencies
pip install -r requirements.txt

# Generate sample data
python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"

# Run it!
python main.py
```

### Web Interface

```bash
streamlit run app/streamlit_app.py
```

---

## Usage

### Python API

```python
from main import MovieRecommender
from preferences.preference_engine import UserPreferences

# Initialize (auto-detects dataset format)
recommender = MovieRecommender('data/movies.csv')

# Get recommendations
results = recommender.get_recommendations("Inception", top_k=5)

# With preferences
prefs = UserPreferences(
    preferred_genres=['Sci-Fi', 'Action'],
    min_rating=7.0
)
results = recommender.get_recommendations("Inception", prefs, top_k=5)
```

### CLI

```bash
# Basic
python cli/app.py --movie "The Matrix" --top 5

# With preferences
python cli/app.py --movie "Inception" --genres "Sci-Fi,Action" --min-rating 8.0
```

---

## Using Your Own Dataset

### Option 1: Auto-Detection (Easiest!)

```python
# System automatically detects format
recommender = MovieRecommender('your_movies.csv')
```

### Option 2: Pre-Configured Formats

```python
from ingestion.data_config import TMDBConfig, IMDBConfig, MovieLensConfig

# For TMDB format
recommender = MovieRecommender('movies.csv', config=TMDBConfig())
```

### Option 3: Custom Dataset

```python
from ingestion.data_config import DataConfig

config = DataConfig(
    movie_id_col='film_id',        # Your column names
    title_col='movie_title',
    genres_col='categories',
    overview_col='description',
    language_col='lang',
    rating_col='score'
)

recommender = MovieRecommender('custom.csv', config=config)
```

### Required CSV Columns

Your dataset needs these fields (with any column names):
- **movie_id** - Unique identifier
- **title** - Movie name
- **genres** - Genres (comma/JSON/pipe-separated)
- **overview** - Plot description
- **language** - Language code
- **rating** - Rating (any scale 0-5, 0-10, 0-100)

**Optional:** release_date, popularity, vote_count, runtime

---

## ️ Architecture

```
┌─────────────┐
│   Models    │  Canonical Movie schema
└──────┬──────┘
       │
┌──────▼──────┐
│  Ingestion  │  Load & validate data (supports any format)
└──────┬──────┘
       │
┌──────▼──────┐
│  Features   │  TF-IDF + genre encoding
└──────┬──────┘
       │
┌──────▼──────┐
│ Similarity  │  Cosine similarity computation
└──────┬──────┘
       │
┌──────▼──────┐
│ Preferences │  Soft weighting & personalization
└──────┬──────┘
       │
┌──────▼──────┐
│    Main     │  Orchestration & API
└─────────────┘
```

**Key Design Principles:**
- **Separation of Concerns** - Each layer has single responsibility
- **Testability** - Pure functions, dependency injection
- **Extensibility** - Easy to swap components or add features
- **Type Safety** - Full type hints throughout

---

## Dataset Support

| Format | Description | Auto-Detect | Config |
|--------|-------------|-------------|--------|
| **TMDB** | The Movie Database (JSON genres) | ✅ Yes | `TMDBConfig()` |
| **IMDB** | IMDB exports | ✅ Yes | `IMDBConfig()` |
| **MovieLens** | MovieLens (pipe-separated) | ✅ Yes | `MovieLensConfig()` |
| **Custom** | Any format with mapping | ⚙️ Manual | `DataConfig(...)` |

### Supported Genre Formats
- ✅ Comma-separated: `"Action, Drama, Thriller"`
- ✅ JSON: `[{"name": "Action"}, {"name": "Drama"}]`
- ✅ Pipe-separated: `"Action|Drama|Thriller"`

### Supported Rating Scales
- ✅ 0-10 (e.g., TMDB, IMDB)
- ✅ 0-5 (e.g., user ratings)
- ✅ 0-100 (e.g., Rotten Tomatoes)
- ✅ Custom normalizers

---

## Project Structure

```
CineSense/
├── models/              # Data schemas (Movie dataclass)
├── ingestion/           # Data loading with format detection
│   ├── loader.py       # Main data loader
│   └── data_config.py  # Format configurations
├── features/            # Feature engineering (TF-IDF)
├── similarity/          # Similarity computation
├── preferences/         # User preference handling
├── cli/                 # Command-line interface
├── app/                 # Streamlit web interface
├── tests/               # Unit & integration tests
├── main.py             # Main orchestrator
└── requirements.txt    # Dependencies
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## Deployment

### Streamlit Cloud (Free)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Set main file: `app/streamlit_app.py`
5. Deploy!

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app/streamlit_app.py"]
```

```bash
docker build -t CineSense .
docker run -p 8501:8501 movie-recommender
```

---

## Configuration

### Feature Builder

```python
from features.feature_builder import FeatureBuilder

builder = FeatureBuilder(
    max_features=5000,    # Max TF-IDF features
    ngram_range=(1, 2),   # Unigrams + bigrams
    min_df=1              # Min document frequency
)
```

### User Preferences

```python
from preferences.preference_engine import UserPreferences

prefs = UserPreferences(
    preferred_genres=['Action', 'Sci-Fi'],
    preferred_languages=['en'],
    genre_weight=0.3,      # Genre boost multiplier
    language_weight=0.2,   # Language boost multiplier
    min_rating=7.0         # Soft rating filter
)
```

---
