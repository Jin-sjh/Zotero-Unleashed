"""
Natural Language Processing Utilities for Zotero AI Features

This module provides NLP functionalities for:
- Text preprocessing
- Tag generation
- Research field classification
"""

import re
from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch


class NLPUtils:
    def __init__(self):
        # Initialize sentence transformer model for embeddings
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize keyword extraction pipeline
        try:
            self.keyword_extractor = pipeline(
                "token-classification",
                model="Davlan/bert-base-multilingual-cased-ner-hrl"
            )
        except:
            # Fallback if model fails to load
            self.keyword_extractor = None
        
        # Predefined research fields for classification
        self.research_fields = {
            'computer_science': ['algorithm', 'machine learning', 'artificial intelligence', 'data science', 
                                'software engineering', 'computer vision', 'natural language processing', 
                                'cybersecurity', 'database', 'network', 'programming'],
            'biology': ['cell', 'gene', 'protein', 'dna', 'rna', 'enzyme', 'organism', 'evolution', 
                       'ecology', 'genetics', 'microbiology', 'biochemistry', 'molecular biology'],
            'medicine': ['patient', 'clinical', 'therapy', 'diagnosis', 'treatment', 'disease', 
                        'pharmacology', 'surgery', 'symptom', 'medical', 'healthcare', 'drug'],
            'physics': ['quantum', 'particle', 'energy', 'motion', 'gravity', 'electromagnetic', 
                       'thermodynamics', 'optics', 'relativity', 'atom', 'molecule', 'wave'],
            'chemistry': ['compound', 'reaction', 'molecule', 'bond', 'catalyst', 'solution', 
                         'acid', 'base', 'organic', 'inorganic', 'chemical', 'element'],
            'mathematics': ['theorem', 'proof', 'equation', 'function', 'calculus', 'algebra', 
                           'geometry', 'statistics', 'probability', 'analysis', 'number theory'],
            'environmental_science': ['climate', 'pollution', 'sustainability', 'ecosystem', 
                                    'biodiversity', 'conservation', 'carbon', 'emission', 
                                    'renewable energy', 'green', 'environment']
        }

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for NLP tasks
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespaces
        text = ' '.join(text.split())
        
        return text

    def generate_tags(self, text: str) -> List[str]:
        """
        Generate relevant tags for literature based on content
        
        Args:
            text: Text content of the literature item
            
        Returns:
            List of generated tags
        """
        if not text:
            return []
        
        processed_text = self.preprocess_text(text)
        tokens = processed_text.split()
        
        # Extract potential keywords based on frequency and length
        word_freq = {}
        for token in tokens:
            if len(token) > 3:  # Only consider words longer than 3 characters
                word_freq[token] = word_freq.get(token, 0) + 1
        
        # Get top frequent words as potential tags
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, freq in sorted_words[:10]]  # Top 10 frequent words
        
        # If keyword extractor is available, use it to enhance tags
        if self.keyword_extractor:
            try:
                entities = self.keyword_extractor(text[:512])  # Limit text length for model
                entity_words = [entity['word'].lower().strip('##') for entity in entities 
                               if entity['score'] > 0.5]
                top_words.extend(entity_words)
            except:
                pass  # Fallback to basic method if extraction fails
        
        # Remove duplicates while preserving order
        unique_tags = []
        for tag in top_words:
            if tag not in unique_tags and len(unique_tags) < 10:
                unique_tags.append(tag)
        
        return unique_tags

    def classify_research_field(self, text: str) -> str:
        """
        Classify the research field of literature based on content
        
        Args:
            text: Text content of the literature item
            
        Returns:
            Classified research field
        """
        if not text:
            return "unknown"
        
        processed_text = self.preprocess_text(text)
        tokens = set(processed_text.split())  # Use set to avoid counting duplicates
        
        field_scores = {}
        
        # Calculate score for each research field based on keyword matches
        for field, keywords in self.research_fields.items():
            score = 0
            for keyword in keywords:
                if keyword in tokens:
                    score += 1
            field_scores[field] = score
        
        # Return the field with highest score, or 'unknown' if no matches
        if max(field_scores.values()) > 0:
            return max(field_scores, key=field_scores.get)
        else:
            return "unknown"

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Generate embeddings for both texts
        embeddings = self.sentence_model.encode([text1, text2])
        
        # Calculate cosine similarity
        embedding1 = embeddings[0]
        embedding2 = embeddings[1]
        
        # Compute cosine similarity
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        similarity = dot_product / (magnitude1 * magnitude2)
        
        # Ensure similarity is between 0 and 1
        return max(0.0, min(1.0, (similarity + 1) / 2))  # Normalize from [-1,1] to [0,1]

    def extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text
        
        Args:
            text: Input text
            
        Returns:
            List of key phrases
        """
        if not text:
            return []
        
        # Simple approach: extract noun phrases using regex patterns
        # In a real implementation, this would use more sophisticated NLP techniques
        sentences = re.split(r'[.!?]+', text)
        key_phrases = []
        
        for sentence in sentences:
            # Look for common noun phrase patterns
            # This is a simplified approach - real implementation would use POS tagging
            words = sentence.strip().split()
            if len(words) > 2:
                # Take the last few words as potential key phrases
                phrase = ' '.join(words[-3:])  # Last 3 words as phrase
                if len(phrase) > 5:  # Only add phrases longer than 5 characters
                    key_phrases.append(phrase.strip())
        
        # Remove duplicates while preserving order
        unique_phrases = []
        for phrase in key_phrases:
            if phrase not in unique_phrases and len(unique_phrases) < 10:
                unique_phrases.append(phrase)
        
        return unique_phrases