"""
Similarity Engine for Zotero AI Features

This module calculates text similarity for:
- Duplicate detection
- Content comparison
- Related literature identification
"""

from typing import List, Dict, Any, Tuple
from .nlp_utils import NLPUtils
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityEngine:
    def __init__(self):
        self.nlp_utils = NLPUtils()

    def calculate_similarities(self, literature_data: List[Dict[str, Any]]) -> Dict[Tuple[str, str], float]:
        """
        Calculate pairwise similarities between literature items
        
        Args:
            literature_data: List of literature items
            
        Returns:
            Dictionary mapping (item1_id, item2_id) tuples to similarity scores
        """
        if len(literature_data) < 2:
            return {}
        
        # Extract text content for all items
        texts = []
        item_ids = []
        
        for item in literature_data:
            text_content = self.nlp_utils._extract_text_for_analysis(item)
            texts.append(text_content)
            item_ids.append(item['id'])
        
        # Calculate embeddings for all texts
        embeddings = self.nlp_utils.sentence_model.encode(texts)
        
        # Calculate cosine similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Create result dictionary mapping pairs to similarity scores
        results = {}
        for i in range(len(item_ids)):
            for j in range(i+1, len(item_ids)):  # Only calculate upper triangle to avoid duplicates
                pair = (item_ids[i], item_ids[j])
                similarity_score = float(similarity_matrix[i][j])
                results[pair] = similarity_score
                
                # Also add reverse pair for easy lookup
                results[(item_ids[j], item_ids[i])] = similarity_score
        
        return results

    def calculate_pairwise_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        return self.nlp_utils.calculate_text_similarity(text1, text2)

    def find_most_similar_texts(self, target_text: str, candidate_texts: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find the most similar texts to a target text from a list of candidates
        
        Args:
            target_text: Target text to compare against
            candidate_texts: List of candidate texts
            top_k: Number of top similar texts to return
            
        Returns:
            List of tuples (text, similarity_score) for top similar texts
        """
        if not target_text or not candidate_texts:
            return []
        
        # Calculate similarity between target and all candidates
        similarities = []
        for candidate in candidate_texts:
            similarity = self.calculate_pairwise_similarity(target_text, candidate)
            similarities.append((candidate, similarity))
        
        # Sort by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return similarities[:top_k]

    def detect_duplicates_with_threshold(self, literature_data: List[Dict[str, Any]], 
                                       threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Detect duplicate literature entries above a similarity threshold
        
        Args:
            literature_data: List of literature items
            threshold: Minimum similarity threshold for considering items as duplicates
            
        Returns:
            List of duplicate pairs with similarity scores
        """
        similarities = self.calculate_similarities(literature_data)
        
        duplicates = []
        processed_pairs = set()
        
        for (id1, id2), score in similarities.items():
            # Create a canonical pair representation to avoid duplicates
            pair = tuple(sorted([id1, id2]))
            if pair not in processed_pairs and score >= threshold:
                # Find the actual items for their titles
                item1 = next((item for item in literature_data if item['id'] == id1), {})
                item2 = next((item for item in literature_data if item['id'] == id2), {})
                
                duplicates.append({
                    'item1_id': id1,
                    'item1_title': item1.get('title', ''),
                    'item2_id': id2,
                    'item2_title': item2.get('title', ''),
                    'similarity_score': score
                })
                
                processed_pairs.add(pair)
        
        return duplicates