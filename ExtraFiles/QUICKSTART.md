# 🚀 Quick Start Guide - Movie Recommendation Engine

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd movie-recommendation-engine
pip install -r requirements.txt
```

### Step 2: Generate Sample Data
```bash
python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"
```

### Step 3: Test It!
```bash
python main.py
```

You should see output like:
```
✓ System initialized successfully!
Top 5 movies similar to 'The Matrix':
1. Inception - Score: 0.653
2. The Dark Knight - Score: 0.419
...
```

---

## 📱 Try the Interfaces

### CLI
```bash
python cli/app.py --movie "Inception" --top 5
```

### Web App
```bash
streamlit run app/streamlit_app.py
```
Opens at `http://localhost:8501`

---

## 🎯 Common Commands

### Get Recommendations
```bash
# Basic
python cli/app.py --movie "The Matrix"

# With preferences
python cli/app.py --movie "Inception" --genres "Sci-Fi,Action" --min-rating 8.0

# More results
python cli/app.py --movie "Pulp Fiction" --top 10
```

### Use in Python

```python
from main import MovieRecommender
from preferences.preference_engine import UserPreferences

# Initialize
recommender = MovieRecommender('../data/movies.csv')

# Get recommendations
results = recommender.get_recommendations("Inception", top_k=5)

# With preferences
prefs = UserPreferences(
    preferred_genres=['Sci-Fi', 'Action'],
    min_rating=8.0
)
results = recommender.get_recommendations("Inception", prefs, top_k=5)

# Print results
for r in results:
    print(f"{r['title']} - {r['score']:.3f}")
```

---

## 🔧 Using Your Own Data

1. **Prepare CSV** with these columns:
   ```
   movie_id,title,genres,overview,language,rating
   ```

2. **Load it:**
   ```python
   recommender = MovieRecommender('path/to/your_movies.csv')
   ```

That's it!

---

## 📊 What Each File Does

```
├── main.py              # 👈 START HERE - Main orchestrator
├── cli/app.py           # Command-line interface
├── app/streamlit_app.py # Web interface
│
├── models/movie.py      # Movie data structure
├── ingestion/loader.py  # Loads CSV data
├── features/           # Builds ML features
├── similarity/         # Computes similarity
└── preferences/        # Personalizes results
```

---

## 🐛 Troubleshooting

**Error: "FileNotFoundError: data/movies.csv"**
```bash
python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"
```

**Error: "No module named 'sklearn'"**
```bash
pip install -r requirements.txt
```

**Streamlit won't start**
```bash
# Make sure you're in the project root
cd movie-recommendation-engine
streamlit run app/streamlit_app.py
```

---

## ✅ Success Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Sample data created (check `data/movies.csv` exists)
- [ ] Main script runs successfully (`python main.py`)
- [ ] CLI works (`python cli/app.py --movie "The Matrix"`)
- [ ] Web app launches (`streamlit run app/streamlit_app.py`)

---

## 🎓 Next Steps

1. **Read README.md** for full documentation
2. **Check PROJECT_SUMMARY.md** for resume bullets
3. **Review SETUP.md** for deployment options
4. **Explore the code** starting from `main.py`
5. **Run tests** with `pytest tests/`

---

## 🚢 Deploy to GitHub

```bash
cd movie-recommendation-engine
git init
git add .
git commit -m "Initial commit: Movie recommendation engine"
git remote add origin https://github.com/yourusername/movie-recommendation-engine.git
git push -u origin main
```

Then update:
- README.md (add your GitHub username)
- LICENSE (add your name)
- PROJECT_SUMMARY.md (add your details)

---

**Ready to build amazing recommendations!** 🎬✨
