# 📊 Using Your Own Dataset - Complete Guide

This guide shows you how to use the recommendation system with **ANY movie dataset**.

---

## 🎯 Quick Start (Auto-Detection)

The system can **automatically detect** your dataset format!

```python
from main import MovieRecommender

# Just provide your CSV path - it will auto-detect the format!
recommender = MovieRecommender('path/to/your/movies.csv')
```

That's it! The system will:
1. ✅ Detect column names automatically
2. ✅ Parse genres in different formats (comma-separated, JSON, pipe-separated)
3. ✅ Normalize ratings to 0-10 scale
4. ✅ Handle missing data gracefully

---

## 📁 Supported Dataset Formats

### 1. TMDB Format (The Movie Database)

**Columns:** `id`, `title`, `genres`, `overview`, `vote_average`, `original_language`

```python
from ingestion.loader import MovieDataLoader
from ingestion.data_config import TMDBConfig

# Use pre-configured TMDB format
config = TMDBConfig()
loader = MovieDataLoader('tmdb_movies.csv', config=config)
movies = loader.load()
```

**Example row:**
```csv
id,title,genres,overview,vote_average,original_language
19995,Avatar,"[{""name"": ""Action""}, {""name"": ""Adventure""}]",A paraplegic Marine...,7.2,en
```

### 2. IMDB Format

**Columns:** `imdb_id`, `title`, `genres`, `plot`, `imdb_rating`, `language`

```python
from ingestion.data_config import IMDBConfig

config = IMDBConfig()
loader = MovieDataLoader('imdb_movies.csv', config=config)
movies = loader.load()
```

### 3. MovieLens Format

**Columns:** `movieId`, `title`, `genres` (pipe-separated)

```python
from ingestion.data_config import MovieLensConfig

config = MovieLensConfig()
loader = MovieDataLoader('movielens.csv', config=config)
movies = loader.load()
```

**Example row:**
```csv
movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
```

---

## 🛠️ Custom Dataset Configuration

If auto-detection doesn't work, create a custom configuration:

### Step 1: Identify Your Columns

Look at your CSV file and identify which columns contain:
- Movie ID (unique identifier)
- Title
- Genres
- Overview/Plot/Description
- Language
- Rating

### Step 2: Create a DataConfig

```python
from ingestion.data_config import DataConfig
from ingestion.loader import MovieDataLoader

# Map YOUR column names to the required fields
config = DataConfig(
    movie_id_col='my_id_column',      # Your ID column name
    title_col='movie_title',          # Your title column
    genres_col='genre_list',          # Your genres column
    overview_col='description',       # Your overview/plot column
    language_col='lang',              # Your language column
    rating_col='user_rating',         # Your rating column
    # Optional
    release_date_col='year',          # Optional: release date
    popularity_col='popularity_score' # Optional: popularity
)

# Load your data
loader = MovieDataLoader('your_movies.csv', config=config)
movies = loader.load()
```

### Step 3: Handle Special Formats

#### Custom Genre Parser (for unusual formats)

```python
def my_genre_parser(genre_string):
    """Parse genres in your specific format."""
    # Example: "Action;Drama;Thriller"
    if not genre_string:
        return ['Unknown']
    return [g.strip() for g in genre_string.split(';')]

config = DataConfig(
    movie_id_col='id',
    title_col='title',
    genres_col='genres',
    overview_col='summary',
    language_col='language',
    rating_col='score',
    genre_parser=my_genre_parser  # Use custom parser
)
```

#### Custom Rating Normalizer (for different scales)

```python
def normalize_5_star_rating(rating):
    """Convert 5-star rating to 10-point scale."""
    try:
        return float(rating) * 2  # 5 stars -> 10 points
    except:
        return 0.0

config = DataConfig(
    movie_id_col='id',
    title_col='name',
    genres_col='categories',
    overview_col='description',
    language_col='lang',
    rating_col='stars',
    rating_normalizer=normalize_5_star_rating  # Custom normalizer
)
```

---

## 💡 Real-World Examples

### Example 1: Your Uploaded Dataset (TMDB Format)

```python
from main import MovieRecommender
from ingestion.data_config import TMDBConfig

# Your dataset has TMDB format
recommender = MovieRecommender(
    'movies.csv',
    config=TMDBConfig()
)

# Get recommendations
results = recommender.get_recommendations("Avatar", top_k=5)
for rec in results:
    print(f"{rec['title']} - {rec['score']:.3f}")
```

### Example 2: Custom Dataset

Let's say your dataset looks like this:

```csv
film_id,film_name,category,synopsis,spoken_lang,critic_score
1,Some Movie,"Drama,Thriller",A gripping tale...,English,8.5
```

**Configuration:**

```python
from ingestion.data_config import DataConfig
from main import MovieRecommender

config = DataConfig(
    movie_id_col='film_id',
    title_col='film_name',
    genres_col='category',
    overview_col='synopsis',
    language_col='spoken_lang',
    rating_col='critic_score'
)

recommender = MovieRecommender('my_custom_movies.csv', config=config)
```

### Example 3: Rating on Different Scale

If your ratings are 0-5 instead of 0-10:

```python
def scale_to_10(rating):
    return float(rating) * 2  # 5 -> 10

config = DataConfig(
    movie_id_col='id',
    title_col='title',
    genres_col='genres',
    overview_col='plot',
    language_col='language',
    rating_col='rating',
    rating_normalizer=scale_to_10
)
```

---

## 🔧 Using Config with Main Recommender

### Method 1: Pass Config to Recommender

```python
from main import MovieRecommender
from ingestion.data_config import TMDBConfig

config = TMDBConfig()
recommender = MovieRecommender(
    data_path='your_movies.csv',
    config=config  # Pass your config here
)
```

### Method 2: Let Recommender Create Loader

The recommender will use your config automatically:

```python
# In main.py, the recommender accepts a config parameter
recommender = MovieRecommender(
    data_path='movies.csv',
    config=TMDBConfig(),
    rebuild_features=False
)
```

---

## 📋 Required vs Optional Columns

### Required Columns (MUST have):
- ✅ **movie_id**: Unique identifier
- ✅ **title**: Movie name
- ✅ **genres**: Genre information
- ✅ **overview**: Plot summary/description
- ✅ **language**: Language code
- ✅ **rating**: Rating score

### Optional Columns (nice to have):
- 📅 **release_date**: Release date
- 📊 **popularity**: Popularity score
- 🗳️ **vote_count**: Number of votes
- ⏱️ **runtime**: Movie duration

---

## 🐛 Troubleshooting

### Error: "Missing required columns"

**Problem:** Your dataset columns don't match the expected names.

**Solution:** Create a custom `DataConfig` mapping your column names.

```python
# Check your CSV columns first
import pandas as pd
df = pd.read_csv('your_movies.csv')
print(df.columns.tolist())

# Then map them
config = DataConfig(
    movie_id_col='your_actual_id_column',
    # ... map other columns
)
```

### Error: "Could not parse genres"

**Problem:** Genres are in an unusual format.

**Solution:** Create a custom genre parser.

```python
def my_parser(genre_str):
    # Your parsing logic here
    return genre_str.split('|')  # or split(',') or json.loads(), etc.

config = DataConfig(
    # ...
    genre_parser=my_parser
)
```

### Error: "Ratings are weird"

**Problem:** Ratings are on a different scale (e.g., 0-5, 0-100).

**Solution:** Create a custom rating normalizer.

```python
def normalize_rating(rating):
    # Convert to 0-10 scale
    if rating > 10:  # Assume 0-100 scale
        return rating / 10
    return rating

config = DataConfig(
    # ...
    rating_normalizer=normalize_rating
)
```

---

## ✅ Testing Your Configuration

Before running the full system, test your configuration:

```python
from ingestion.loader import MovieDataLoader
from ingestion.data_config import DataConfig

# Create your config
config = DataConfig(
    movie_id_col='id',
    title_col='title',
    # ... other mappings
)

# Test loading
loader = MovieDataLoader('your_movies.csv', config=config)
movies = loader.load()

# Check results
print(f"Loaded {len(movies)} movies")
print(f"Sample movie: {movies[0]}")
print(f"Genres: {movies[0].genres}")
print(f"Rating: {movies[0].rating}")
```

---

## 🎓 Advanced: Handling Complex Formats

### JSON Genres

If genres are stored as JSON:
```json
[{"id": 28, "name": "Action"}, {"id": 18, "name": "Drama"}]
```

The default parser handles this automatically! No custom parser needed.

### Multiple Languages

If multiple languages are stored:
```json
[{"iso_639_1": "en", "name": "English"}, {"iso_639_1": "es", "name": "Spanish"}]
```

Custom parser:
```python
import json

def parse_first_language(lang_string):
    try:
        languages = json.loads(lang_string)
        if languages and isinstance(languages, list):
            return languages[0].get('iso_639_1', 'en')
    except:
        pass
    return 'en'

# Use in your preprocessing step
```

---

## 📦 Complete Working Example

Here's a full example from start to finish:

```python
# 1. Import required modules
from main import MovieRecommender
from ingestion.data_config import DataConfig, TMDBConfig
from preferences.preference_engine import UserPreferences

# 2. Configure for your dataset
# Option A: Use pre-configured format
config = TMDBConfig()

# Option B: Custom configuration
config = DataConfig(
    movie_id_col='id',
    title_col='title',
    genres_col='genres',
    overview_col='overview',
    language_col='original_language',
    rating_col='vote_average'
)

# 3. Initialize recommender
recommender = MovieRecommender(
    data_path='your_movies.csv',
    config=config
)

# 4. Set preferences (optional)
prefs = UserPreferences(
    preferred_genres=['Action', 'Sci-Fi'],
    min_rating=7.0
)

# 5. Get recommendations
results = recommender.get_recommendations(
    movie_title="Avatar",
    preferences=prefs,
    top_k=10
)

# 6. Display results
for i, rec in enumerate(results, 1):
    print(f"{i}. {rec['title']}")
    print(f"   Score: {rec['score']:.3f}")
    print(f"   Rating: {rec['rating']}/10")
    print(f"   Genres: {', '.join(rec['genres'])}")
    print()
```

---

## 🚀 Next Steps

1. ✅ Identify your dataset format
2. ✅ Create appropriate `DataConfig`
3. ✅ Test with a small sample first
4. ✅ Run full recommendation system
5. ✅ Deploy with Streamlit!

**Need help?** Check the examples in `ingestion/data_config.py` or open an issue on GitHub!
