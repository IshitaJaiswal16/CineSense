# 🚀 Using Your TMDB Dataset (4800+ Movies)

Your uploaded `movies.csv` contains **4803 movies** in TMDB format. Here's how to use it:

## ⚡ Quick Start

### Step 1: Place Your Dataset

Copy `movies.csv` to the project's `data` folder:

```bash
cp movies.csv movie-recommendation-engine/data/
```

Or place it anywhere and reference the path.

### Step 2: Run with TMDB Config

```python
from main import MovieRecommender
from ingestion.data_config import TMDBConfig

# Initialize with TMDB format
recommender = MovieRecommender(
    data_path='../data/movies.csv',  # Your dataset
    config=TMDBConfig()  # TMDB configuration
)

# Get recommendations
results = recommender.get_recommendations("Avatar", top_k=5)

for rec in results:
    print(f"{rec['title']} - Score: {rec['score']:.3f}")
```

## 🎬 Run the Example

```bash
cd movie-recommendation-engine
python example_tmdb.py
```

This will show you:
- ✅ Basic recommendations
- ✅ Personalized recommendations with preferences
- ✅ Dataset statistics
- ✅ Top rated movies

## 🌐 Use with Streamlit

```bash
# Copy your dataset
cp movies.csv data/

# Update streamlit app to use TMDB config
streamlit run app/streamlit_app.py
```

The app will auto-detect the TMDB format!

## 🔧 Your Dataset Structure

Your `movies.csv` has these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Movie ID | 19995 |
| `title` | Movie name | Avatar |
| `genres` | Genres (JSON format) | `[{"name": "Action"}]` |
| `overview` | Plot description | "In the 22nd century..." |
| `vote_average` | Rating (0-10) | 7.2 |
| `original_language` | Language code | en |
| `popularity` | Popularity score | 150.437 |
| `vote_count` | Number of votes | 12114 |
| `runtime` | Duration (minutes) | 162 |
| `release_date` | Release date | 2009-12-10 |

## ✨ What Makes This Different?

With 4800+ movies, you can:

1. **Better Recommendations** - More data = better similarity matching
2. **More Genres** - Explore diverse movie categories
3. **Real Dataset** - Industry-standard TMDB format
4. **Production-Ready** - Same format used by streaming platforms

## 💡 Example Queries to Try

```python
# Action blockbusters
recommender.get_recommendations("Avatar", top_k=10)

# Dark thrillers
recommender.get_recommendations("The Dark Knight", top_k=10)

# Animated films
recommender.get_recommendations("Toy Story", top_k=10)

# Sci-fi classics
recommender.get_recommendations("Inception", top_k=10)
```

## 🎯 With Preferences

```python
from preferences.preference_engine import UserPreferences

# High-rated action movies
prefs = UserPreferences(
    preferred_genres=['Action', 'Adventure'],
    min_rating=7.5
)

results = recommender.get_recommendations(
    "Avatar",
    preferences=prefs,
    top_k=10
)
```

## 📊 Performance Tips

For 4800+ movies:

1. **First run**: Takes ~30 seconds to build features
2. **Subsequent runs**: <5 seconds (uses cache)
3. **Rebuild cache**: Only if you modify the dataset

```python
# Force rebuild (if dataset changes)
recommender = MovieRecommender(
    'data/movies.csv',
    config=TMDBConfig(),
    rebuild_features=True  # Rebuild cache
)
```

## 🐛 Troubleshooting

### Issue: "FileNotFoundError"
**Solution:** Make sure `movies.csv` is in the correct path:
```bash
ls data/movies.csv  # Should exist
```

### Issue: "Memory Error"
**Solution:** Reduce feature dimensions:
```python
from features.feature_builder import FeatureBuilder

builder = FeatureBuilder(
    max_features=1000,  # Reduce from 5000
    min_df=5           # Increase min frequency
)
```

### Issue: Slow Performance
**Solution:** Features are cached after first run. Subsequent runs are much faster!

---

**Ready to build amazing recommendations with 4800+ movies!** 🎉
