# AI module initialization

from .llm_client import OpenAICompatibleClient
from .ai_processor import AIProcessor, ai_processor
from .nlp_utils import NLPUtils
from .clustering_engine import ClusteringEngine
from .similarity_engine import SimilarityEngine

def get_ai_processor():
    return ai_processor

__all__ = [
    "OpenAICompatibleClient",
    "AIProcessor",
    "ai_processor",
    "NLPUtils",
    "ClusteringEngine",
    "SimilarityEngine",
    "get_ai_processor"
]
