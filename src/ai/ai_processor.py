"""
AI Processor Module for Zotero Literature Organization

This module handles AI-driven literature organization tasks including:
- Automatic tagging
- Research field classification
- Duplicate detection
- Content clustering
"""

import asyncio
from typing import Dict, List, Optional, Any
from .nlp_utils import NLPUtils
from .similarity_engine import SimilarityEngine
from .clustering_engine import ClusteringEngine
from ..core.db_connector import ZoteroDB
from .llm_client import OpenAICompatibleClient


class AIProcessor:
    def __init__(self, db_path: Optional[str] = None):
        self.nlp_utils = NLPUtils()
        self.similarity_engine = SimilarityEngine()
        self.clustering_engine = ClusteringEngine()
        self.db_connector = ZoteroDB(db_path) if db_path else None
        self.llm_client = OpenAICompatibleClient()

    def set_db_path(self, db_path: str):
        """Set or update the database path"""
        self.db_connector = ZoteroDB(db_path)

    async def auto_tag_literature(self, collection_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Automatically tag literature based on content analysis
        
        Args:
            collection_id: ID of the Zotero collection to process
            options: Additional options for tagging
            
        Returns:
            Dictionary containing tagging results
        """
        if not self.db_connector:
            raise ValueError("Database connector not initialized. Call set_db_path() first.")
        
        # Fetch literature from the specified collection
        literature_data = self.db_connector.get_collection_items(collection_id)
        
        results = {
            'processed_count': 0,
            'success_count': 0,
            'failed_count': 0,
            'results': []
        }
        
        for item in literature_data:
            try:
                # Extract text content for analysis
                text_content = self._extract_text_for_analysis(item)
                
                # Generate tags using NLP utilities
                tags = self.nlp_utils.generate_tags(text_content)
                
                # Note: Zotero database is read-only in this implementation
                # Tags would need to be applied through Zotero API or direct DB modification
                results['results'].append({
                    'item_id': item.get('itemID'),
                    'title': self._get_item_title(item),
                    'generated_tags': tags,
                    'success': True
                })
                
                results['processed_count'] += 1
                results['success_count'] += 1
                    
            except Exception as e:
                results['failed_count'] += 1
                results['results'].append({
                    'item_id': item.get('itemID'),
                    'title': self._get_item_title(item),
                    'error': str(e),
                    'success': False
                })
        
        return results

    def _get_item_title(self, item: Dict[str, Any]) -> str:
        """Get item title from metadata"""
        if not self.db_connector:
            return 'Unknown'
        try:
            metadata = self.db_connector.get_item_metadata(item.get('itemID'))
            return metadata.get('title', 'Unknown')
        except:
            return 'Unknown'

    async def classify_by_research_field(self, collection_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify literature by research field based on content analysis
        
        Args:
            collection_id: ID of the Zotero collection to process
            options: Additional options for classification
            
        Returns:
            Dictionary containing classification results
        """
        if not self.db_connector:
            raise ValueError("Database connector not initialized. Call set_db_path() first.")
        
        # Fetch literature from the specified collection
        literature_data = self.db_connector.get_collection_items(collection_id)
        
        results = {
            'processed_count': 0,
            'success_count': 0,
            'failed_count': 0,
            'results': []
        }
        
        for item in literature_data:
            try:
                # Extract text content for analysis
                text_content = self._extract_text_for_analysis(item)
                
                # Classify research field using NLP utilities
                research_field = self.nlp_utils.classify_research_field(text_content)
                
                # Note: Classification results are returned but not written to DB
                results['results'].append({
                    'item_id': item.get('itemID'),
                    'title': self._get_item_title(item),
                    'research_field': research_field,
                    'success': True
                })
                
                results['processed_count'] += 1
                results['success_count'] += 1
                    
            except Exception as e:
                results['failed_count'] += 1
                results['results'].append({
                    'item_id': item.get('itemID'),
                    'title': self._get_item_title(item),
                    'error': str(e),
                    'success': False
                })
        
        return results

    async def detect_duplicates(self, collection_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect potential duplicate literature entries
        
        Args:
            collection_id: ID of the Zotero collection to process
            options: Additional options for duplicate detection (e.g., threshold)
            
        Returns:
            Dictionary containing duplicate detection results
        """
        if not self.db_connector:
            raise ValueError("Database connector not initialized. Call set_db_path() first.")
        
        # Set default threshold if not provided
        threshold = options.get('threshold', 0.8) if options else 0.8
        
        # Fetch literature from the specified collection
        literature_data = self.db_connector.get_collection_items(collection_id)
        
        # Calculate similarities between items
        similarity_results = self.similarity_engine.calculate_similarities(literature_data)
        
        duplicates = []
        processed_pairs = set()
        
        for i, item1 in enumerate(literature_data):
            for j, item2 in enumerate(literature_data):
                if i != j:
                    item1_id = item1.get('itemID')
                    item2_id = item2.get('itemID')
                    pair = tuple(sorted([item1_id, item2_id]))
                    if pair not in processed_pairs:
                        processed_pairs.add(pair)
                        
                        similarity_score = similarity_results.get((item1_id, item2_id), 0)
                        if similarity_score >= threshold:
                            duplicates.append({
                                'item1_id': item1_id,
                                'item1_title': self._get_item_title(item1),
                                'item2_id': item2_id,
                                'item2_title': self._get_item_title(item2),
                                'similarity_score': similarity_score
                            })
        
        results = {
            'total_items': len(literature_data),
            'duplicate_pairs': len(duplicates),
            'duplicates': duplicates
        }
        
        return results

    async def cluster_content(self, collection_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Cluster literature based on content similarity
        
        Args:
            collection_id: ID of the Zotero collection to process
            options: Additional options for clustering (e.g., number of clusters)
            
        Returns:
            Dictionary containing clustering results
        """
        if not self.db_connector:
            raise ValueError("Database connector not initialized. Call set_db_path() first.")
        
        # Fetch literature from the specified collection
        literature_data = self.db_connector.get_collection_items(collection_id)
        
        # Extract text content for clustering
        texts = []
        item_ids = []
        for item in literature_data:
            text_content = self._extract_text_for_analysis(item)
            texts.append(text_content)
            item_ids.append(item.get('itemID'))
        
        # Perform clustering
        cluster_labels = self.clustering_engine.perform_clustering(texts, options)
        
        # Organize results by cluster
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            cluster_id = f"cluster_{label}"
            if cluster_id not in clusters:
                clusters[cluster_id] = {
                    'cluster_label': label,
                    'item_count': 0,
                    'items': []
                }
            
            # Add item to cluster
            item_data = {
                'id': item_ids[idx],
                'title': self._get_item_title(literature_data[idx])
            }
            clusters[cluster_id]['items'].append(item_data)
            clusters[cluster_id]['item_count'] += 1
        
        results = {
            'total_clusters': len(clusters),
            'clusters': clusters,
            'total_items': len(literature_data)
        }
        
        return results

    def _extract_text_for_analysis(self, item: Dict[str, Any]) -> str:
        """
        Extract text content from a literature item for AI analysis
        
        Args:
            item: Literature item dictionary from ZoteroDB
            
        Returns:
            Combined text content for analysis
        """
        if not self.db_connector:
            return ""
        
        text_parts = []
        
        try:
            # Get metadata from database
            item_id = item.get('itemID')
            if item_id:
                metadata = self.db_connector.get_item_metadata(item_id)
                
                # Add title
                if metadata.get('title'):
                    text_parts.append(f"Title: {metadata['title']}")
                
                # Add author
                if metadata.get('author'):
                    text_parts.append(f"Author: {metadata['author']}")
                
                # Add date
                if metadata.get('date'):
                    text_parts.append(f"Date: {metadata['date']}")
        except Exception as e:
            # If metadata extraction fails, return minimal info
            pass
        
        return ' '.join(text_parts) if text_parts else "No metadata available"

    async def enhanced_summarize_literature(self, collection_id: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        使用大语言模型增强文献摘要和分析
        
        Args:
            collection_id: 要处理的Zotero集合ID
            options: 其他选项（如摘要长度、分析深度等）
            
        Returns:
            包含摘要结果的字典
        """
        if not self.db_connector:
            raise ValueError("Database connector not initialized. Call set_db_path() first.")
        
        # 获取文献数据
        literature_data = self.db_connector.get_collection_items(collection_id)
        
        results = {
            'processed_count': 0,
            'success_count': 0,
            'failed_count': 0,
            'results': []
        }
        
        for item in literature_data:
            try:
                # 提取文本内容进行分析
                text_content = self._extract_text_for_analysis(item)
                
                # 生成摘要的系统提示
                system_prompt = "你是一个专业的学术文献分析助手。请对提供的文献内容进行简洁准确的摘要。"
                
                # 用户提示，包含实际文献内容
                user_prompt = f"请为以下学术文献生成摘要：\n{text_content[:2000]}"  # 限制长度避免超出API限制
                
                # 使用大语言模型生成摘要
                summary = self.llm_client.generate(prompt=user_prompt, system_prompt=system_prompt)
                
                results['results'].append({
                    'item_id': item.get('itemID'),
                    'title': self._get_item_title(item),
                    'summary': summary,
                    'success': True
                })
                
                results['processed_count'] += 1
                results['success_count'] += 1
                    
            except Exception as e:
                results['failed_count'] += 1
                results['results'].append({
                    'item_id': item.get('itemID'),
                    'title': self._get_item_title(item),
                    'error': str(e),
                    'success': False
                })
        
        return results


# Global AI processor instance (will be initialized with db_path when needed)
ai_processor = AIProcessor()