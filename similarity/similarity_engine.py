"""
Similarity Engine Module
Responsibilities:
- Compute similarity scores between vectors
- Return ranked candidates
- Pure vector operations (no domain knowledge)

This layer is agnostic to what the vectors represent.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityEngine:
    """
    Computes similarity between feature vectors.
    Domain-agnostic: only knows about vectors and scores.
    """
    
    def __init__(self, feature_matrix: np.ndarray):
        """
        Initialize the similarity engine.
        
        Args:
            feature_matrix: Pre-computed feature matrix (n_items, n_features)
        """
        self.feature_matrix = feature_matrix
        self.n_items = feature_matrix.shape[0]
        logger.info(f"Similarity engine initialized with {self.n_items} items")
    
    def compute_similarity_matrix(self) -> np.ndarray:
        """
        Pre-compute full similarity matrix.
        Useful for small datasets or when multiple queries are expected.
        
        Returns:
            Similarity matrix (n_items, n_items)
        """
        logger.info("Computing full similarity matrix...")
        similarity_matrix = cosine_similarity(self.feature_matrix)
        logger.info(f"✓ Similarity matrix computed: {similarity_matrix.shape}")
        return similarity_matrix
    
    def find_similar_items(
        self,
        query_index: int,
        top_k: int = 10,
        exclude_self: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Find most similar items to a query item.
        
        Args:
            query_index: Index of the query item
            top_k: Number of similar items to return
            exclude_self: Whether to exclude the query item itself
            
        Returns:
            List of (index, similarity_score) tuples, sorted by score descending
        """
        if query_index < 0 or query_index >= self.n_items:
            raise ValueError(f"Query index {query_index} out of bounds [0, {self.n_items})")
        
        # Get query vector
        query_vector = self.feature_matrix[query_index].reshape(1, -1)
        
        # Compute similarities
        similarities = cosine_similarity(query_vector, self.feature_matrix)[0]
        
        # Create index-score pairs
        scored_items = [(idx, score) for idx, score in enumerate(similarities)]
        
        # Exclude self if requested
        if exclude_self:
            scored_items = [(idx, score) for idx, score in scored_items if idx != query_index]
        
        # Sort by score descending
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k
        return scored_items[:top_k]
    
    def batch_find_similar_items(
        self,
        query_indices: List[int],
        top_k: int = 10
    ) -> List[List[Tuple[int, float]]]:
        """
        Find similar items for multiple queries efficiently.
        
        Args:
            query_indices: List of query item indices
            top_k: Number of similar items per query
            
        Returns:
            List of results, one per query
        """
        results = []
        for query_idx in query_indices:
            similar_items = self.find_similar_items(query_idx, top_k)
            results.append(similar_items)
        return results
    
    def get_similarity_score(self, index_a: int, index_b: int) -> float:
        """
        Get similarity score between two specific items.
        
        Args:
            index_a: First item index
            index_b: Second item index
            
        Returns:
            Similarity score between 0 and 1
        """
        vector_a = self.feature_matrix[index_a].reshape(1, -1)
        vector_b = self.feature_matrix[index_b].reshape(1, -1)
        
        return cosine_similarity(vector_a, vector_b)[0, 0]


class HybridSimilarityEngine(SimilarityEngine):
    """
    Extended similarity engine that supports weighted combinations
    of different feature types.
    """
    
    def __init__(
        self,
        feature_matrix: np.ndarray,
        feature_weights: dict = None
    ):
        """
        Initialize hybrid similarity engine.
        
        Args:
            feature_matrix: Feature matrix
            feature_weights: Dict mapping feature type to weight
        """
        super().__init__(feature_matrix)
        self.feature_weights = feature_weights or {}
    
    def compute_weighted_similarity(
        self,
        query_index: int,
        text_features_slice: slice,
        genre_features_slice: slice,
        text_weight: float = 0.7,
        genre_weight: float = 0.3
    ) -> np.ndarray:
        """
        Compute weighted similarity using different feature subsets.
        
        Args:
            query_index: Index of query item
            text_features_slice: Slice for text features
            genre_features_slice: Slice for genre features
            text_weight: Weight for text similarity
            genre_weight: Weight for genre similarity
            
        Returns:
            Combined similarity scores
        """
        # Extract feature subsets
        text_features = self.feature_matrix[:, text_features_slice]
        genre_features = self.feature_matrix[:, genre_features_slice]
        
        # Compute separate similarities
        query_text = text_features[query_index].reshape(1, -1)
        query_genre = genre_features[query_index].reshape(1, -1)
        
        text_sim = cosine_similarity(query_text, text_features)[0]
        genre_sim = cosine_similarity(query_genre, genre_features)[0]
        
        # Weighted combination
        combined_sim = (text_weight * text_sim) + (genre_weight * genre_sim)
        
        return combined_sim


if __name__ == "__main__":
    # Example usage
    from ingestion.loader import MovieDataLoader, create_sample_dataset
    from features.feature_builder import FeatureBuilder
    
    # Setup
    create_sample_dataset()
    loader = MovieDataLoader('data/movies.csv')
    movies = loader.load()
    
    builder = FeatureBuilder()
    feature_matrix = builder.build_features(movies)
    
    # Create similarity engine
    engine = SimilarityEngine(feature_matrix)
    
    # Find similar movies
    query_movie = movies[0]  # The Matrix
    query_idx = builder.get_movie_index(query_movie.movie_id)
    
    similar = engine.find_similar_items(query_idx, top_k=5)
    
    print(f"\n{'='*60}")
    print(f"Movies similar to '{query_movie.title}':")
    print(f"{'='*60}")
    
    for idx, score in similar:
        movie_id = builder.get_movie_id(idx)
        similar_movie = next(m for m in movies if m.movie_id == movie_id)
        print(f"\n  {similar_movie.title}")
        print(f"    Similarity: {score:.3f}")
        print(f"    Genres: {', '.join(similar_movie.genres)}")
        print(f"    Rating: {similar_movie.rating}")
