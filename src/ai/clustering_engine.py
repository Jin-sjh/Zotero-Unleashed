"""
Clustering Engine for Zotero AI Features

This module performs content-based clustering of literature using:
- Various clustering algorithms
- Automatic optimal cluster determination
- Text similarity calculations
"""

from typing import List, Dict, Any
from .nlp_utils import NLPUtils
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


class ClusteringEngine:
    def __init__(self):
        self.nlp_utils = NLPUtils()

    def perform_clustering(self, texts: List[str], options: Dict[str, Any] = None) -> List[int]:
        """
        Perform clustering on a list of texts
        
        Args:
            texts: List of text documents to cluster
            options: Clustering options (algorithm, number of clusters, etc.)
            
        Returns:
            List of cluster labels for each text
        """
        if not texts:
            return []
        
        # Default options
        if options is None:
            options = {}
        
        algorithm = options.get('algorithm', 'kmeans')
        n_clusters = options.get('n_clusters', None)
        
        # Generate embeddings for all texts
        embeddings = self.nlp_utils.sentence_model.encode(texts)
        
        # Determine number of clusters if not provided
        if n_clusters is None:
            n_clusters = self._determine_optimal_clusters(embeddings, algorithm)
        
        # Perform clustering based on the selected algorithm
        if algorithm == 'kmeans':
            labels = self._perform_kmeans_clustering(embeddings, n_clusters)
        elif algorithm == 'dbscan':
            labels = self._perform_dbscan_clustering(embeddings)
        elif algorithm == 'hierarchical':
            labels = self._perform_hierarchical_clustering(embeddings, n_clusters)
        else:
            # Default to k-means if algorithm is not recognized
            labels = self._perform_kmeans_clustering(embeddings, n_clusters)
        
        return labels

    def _perform_kmeans_clustering(self, embeddings: np.ndarray, n_clusters: int) -> List[int]:
        """
        Perform K-Means clustering on embeddings
        
        Args:
            embeddings: Array of text embeddings
            n_clusters: Number of clusters to create
            
        Returns:
            List of cluster labels
        """
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        return labels.tolist()

    def _perform_dbscan_clustering(self, embeddings: np.ndarray) -> List[int]:
        """
        Perform DBSCAN clustering on embeddings
        
        Args:
            embeddings: Array of text embeddings
            
        Returns:
            List of cluster labels
        """
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        labels = dbscan.fit_predict(embeddings)
        return labels.tolist()

    def _perform_hierarchical_clustering(self, embeddings: np.ndarray, n_clusters: int) -> List[int]:
        """
        Perform Hierarchical clustering on embeddings
        
        Args:
            embeddings: Array of text embeddings
            n_clusters: Number of clusters to create
            
        Returns:
            List of cluster labels
        """
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
        labels = hierarchical.fit_predict(embeddings)
        return labels.tolist()

    def _determine_optimal_clusters(self, embeddings: np.ndarray, algorithm: str = 'kmeans') -> int:
        """
        Determine the optimal number of clusters using various metrics
        
        Args:
            embeddings: Array of text embeddings
            algorithm: Clustering algorithm to optimize for
            
        Returns:
            Optimal number of clusters
        """
        if len(embeddings) < 2:
            return 1
        if len(embeddings) <= 3:
            return min(2, len(embeddings))
        
        # For small datasets, use a reasonable default
        if len(embeddings) < 10:
            return min(3, len(embeddings))
        
        # Try different numbers of clusters and evaluate using silhouette score
        min_clusters = 2
        max_clusters = min(len(embeddings) - 1, 10)  # Don't exceed n-1 clusters
        
        best_n_clusters = min_clusters
        best_score = -1  # Silhouette score ranges from -1 to 1
        
        for n_clusters in range(min_clusters, max_clusters + 1):
            if algorithm == 'kmeans':
                labels = self._perform_kmeans_clustering(embeddings, n_clusters)
            elif algorithm == 'hierarchical':
                labels = self._perform_hierarchical_clustering(embeddings, n_clusters)
            else:
                # For other algorithms, default to kmeans for evaluation
                labels = self._perform_kmeans_clustering(embeddings, n_clusters)
            
            # Skip if all points are assigned to the same cluster
            if len(set(labels)) < 2:
                continue
            
            try:
                score = silhouette_score(embeddings, labels)
                if score > best_score:
                    best_score = score
                    best_n_clusters = n_clusters
            except:
                # Silhouette score calculation failed, skip this clustering
                continue
        
        # Ensure we return a valid number of clusters
        return max(1, min(best_n_clusters, len(embeddings)))

    def visualize_clusters(self, texts: List[str], labels: List[int], save_path: str = None) -> None:
        """
        Visualize clusters using dimensionality reduction
        
        Args:
            texts: Original texts that were clustered
            labels: Cluster labels for each text
            save_path: Path to save the visualization plot
        """
        if not texts or len(set(labels)) < 2:
            return  # Nothing to visualize
        
        # Generate embeddings
        embeddings = self.nlp_utils.sentence_model.encode(texts)
        
        # Reduce dimensions to 2D for visualization
        pca = PCA(n_components=2)
        reduced_embeddings = pca.fit_transform(embeddings)
        
        # Create scatter plot
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=labels, cmap='viridis')
        plt.colorbar(scatter)
        plt.title('Literature Clustering Visualization')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
        
        plt.close()

    def get_cluster_summary(self, texts: List[str], labels: List[int]) -> Dict[str, Any]:
        """
        Generate a summary of the clustering results
        
        Args:
            texts: Original texts that were clustered
            labels: Cluster labels for each text
            
        Returns:
            Summary of clustering results
        """
        if not texts or not labels or len(texts) != len(labels):
            return {}
        
        # Count items per cluster
        cluster_counts = {}
        for label in labels:
            cluster_counts[label] = cluster_counts.get(label, 0) + 1
        
        # Get sample texts for each cluster
        cluster_samples = {}
        for i, (text, label) in enumerate(zip(texts, labels)):
            if label not in cluster_samples:
                cluster_samples[label] = []
            if len(cluster_samples[label]) < 3:  # Store up to 3 samples per cluster
                # Truncate text for display
                sample_text = text[:100] + "..." if len(text) > 100 else text
                cluster_samples[label].append(sample_text)
        
        return {
            'total_items': len(texts),
            'number_of_clusters': len(set(labels)),
            'cluster_sizes': cluster_counts,
            'cluster_samples': cluster_samples,
            'largest_cluster': max(cluster_counts.values()) if cluster_counts else 0,
            'smallest_cluster': min(cluster_counts.values()) if cluster_counts else 0
        }