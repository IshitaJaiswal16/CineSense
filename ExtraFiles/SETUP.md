# Setup & Deployment Guide

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

## 🔧 Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/movie-recommendation-engine.git
cd movie-recommendation-engine
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Sample Data

```bash
python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"
```

This creates a `data/movies.csv` file with 10 sample movies.

### 5. Test the Installation

```bash
# Run the main script
python main.py

# Or test the CLI
python cli/app.py --movie "The Matrix" --top 3
```

## 🌐 Running the Web Interface

### Streamlit App

```bash
streamlit run app/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📊 Using Your Own Dataset

### Required CSV Format

Your CSV must have these columns:

```csv
movie_id,title,genres,overview,language,rating
```

**Optional columns:**
- `release_date`
- `popularity`
- `vote_count`
- Any other metadata (will be stored in `metadata` dict)

### Example

```csv
movie_id,title,genres,overview,language,rating,release_date
1,Inception,"Action, Sci-Fi, Thriller","A thief who steals corporate secrets...",en,8.8,2010-07-16
2,The Matrix,"Action, Sci-Fi","A computer hacker learns about...",en,8.7,1999-03-31
```

### Loading Custom Data

```python
from main import MovieRecommender

# Point to your CSV file
recommender = MovieRecommender('path/to/your/movies.csv')

# Get recommendations
results = recommender.get_recommendations("Inception", top_k=10)
```

## 🧪 Running Tests

```bash
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

## 🚀 Production Deployment

### Option 1: Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file path: `app/streamlit_app.py`
5. Deploy!

### Option 2: Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate sample data
RUN python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t movie-recommender .
docker run -p 8501:8501 movie-recommender
```

### Option 3: Heroku

1. Create `Procfile`:
```
web: streamlit run app/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

## 🔍 Performance Optimization

### For Large Datasets

1. **Enable feature caching:**

```python
recommender = MovieRecommender(
    'data/movies.csv',
    cache_dir='../cache',
    rebuild_features=False  # Use cached features
)
```

2. **Limit feature dimensions:**
```python
from features.feature_builder import FeatureBuilder

builder = FeatureBuilder(
    max_features=1000,  # Reduce from 5000
    min_df=5            # Increase minimum document frequency
)
```

3. **Use batch processing:**
```python
from similarity.similarity_engine import SimilarityEngine

# Pre-compute similarity matrix for frequent queries
engine = SimilarityEngine(feature_matrix)
sim_matrix = engine.compute_similarity_matrix()  # Cache this
```

## 📁 Project Structure

```
movie-recommendation-engine/
│
├── models/              # Data models (Movie schema)
├── ingestion/           # Data loading & validation
├── features/            # Feature engineering
├── similarity/          # Similarity computation
├── preferences/         # User preference handling
├── cli/                 # Command-line interface
├── app/                 # Web interfaces
├── tests/               # Unit & integration tests
├── data/                # Data files (gitignored)
├── cache/               # Feature cache (gitignored)
│
├── main.py             # Main orchestrator
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore rules
└── LICENSE             # MIT License
```

## 🐛 Troubleshooting

### Issue: "FileNotFoundError: data/movies.csv"

**Solution:** Generate sample data:
```bash
python -c "from ingestion.loader import create_sample_dataset; create_sample_dataset()"
```

### Issue: "ModuleNotFoundError"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Streamlit shows blank page

**Solution:** Check the terminal for errors and ensure:
```bash
# Correct path to streamlit app
streamlit run app/streamlit_app.py

# Not just "streamlit run streamlit_app.py"
```

### Issue: Out of memory on large datasets

**Solution:** Reduce feature dimensions:
```python
builder = FeatureBuilder(max_features=500, min_df=10)
```

## 📚 Additional Resources

- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🤝 Getting Help

- Open an issue on GitHub
- Check existing issues for solutions
- Read the full README.md

## ✅ Verification Checklist

Before deploying, ensure:

- [ ] All tests pass (`pytest tests/`)
- [ ] Sample data generates successfully
- [ ] CLI interface works
- [ ] Streamlit app runs locally
- [ ] README is updated with your info
- [ ] License is appropriate
- [ ] Requirements.txt is complete
- [ ] .gitignore includes cache/ and data/

---

🎉 **You're all set!** Start building amazing recommendations!
