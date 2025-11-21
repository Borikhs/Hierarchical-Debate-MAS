"""
MedRAG Retriever - Medical Document Retrieval System

A standalone retrieval package extracted from MedRAG for medical document search.
This package focuses solely on retrieval functionality without LLM generation.

Based on: https://github.com/Teddy-XiongGZ/MedRAG
Paper: https://arxiv.org/abs/2402.13178
"""

__version__ = "1.0.0"
__author__ = "MedRAG Team (Adapted for standalone use)"

# Import core classes from the existing code
from .core import (
    Retriever,
    RetrievalSystem,
    DocExtracter,
    corpus_names,
    retriever_names,
    embed,
    construct_index
)

# Import configuration
from .config import (
    DEFAULT_CONFIG,
    RETRIEVER_OPTIONS,
    CORPUS_OPTIONS,
    SYSTEM_REQUIREMENTS,
    PERFORMANCE_PRESETS,
    get_retriever_info,
    get_corpus_info,
    get_preset_config,
    list_retrievers,
    list_corpora,
    list_presets
)

# Import preprocessing utilities
from .preprocessing import (
    process_statpearls_corpus,
    extract,
    extract_text,
    concat
)

# Convenience imports
__all__ = [
    # Core classes
    "Retriever",
    "RetrievalSystem",
    "DocExtracter",
    "MedRAGRetriever",

    # Configuration
    "DEFAULT_CONFIG",
    "RETRIEVER_OPTIONS",
    "CORPUS_OPTIONS",
    "SYSTEM_REQUIREMENTS",
    "PERFORMANCE_PRESETS",

    # Helper functions
    "get_retriever_info",
    "get_corpus_info",
    "get_preset_config",
    "list_retrievers",
    "list_corpora",
    "list_presets",

    # Data structures
    "corpus_names",
    "retriever_names",

    # Advanced functions
    "embed",
    "construct_index",

    # Preprocessing utilities
    "process_statpearls_corpus",
    "extract",
    "extract_text",
    "concat"
]


class MedRAGRetriever:
    """
    High-level API for MedRAG Retriever.

    This class provides a simple interface for medical document retrieval
    using the MedRAG system without LLM generation capabilities.

    Example:
        >>> from medrag_retriever import MedRAGRetriever
        >>> retriever = MedRAGRetriever(retriever_name="MedCPT", corpus_name="Textbooks")
        >>> documents, scores = retriever.search("What are the symptoms of diabetes?", k=5)
        >>> for doc, score in zip(documents, scores):
        ...     print(f"Score: {score:.4f}, Title: {doc['title']}")

    Args:
        retriever_name: Name of the retriever to use. Options: "BM25", "Contriever",
                       "SPECTER", "MedCPT", "RRF-2", "RRF-4"
        corpus_name: Name of the corpus to search. Options: "Textbooks", "PubMed",
                    "StatPearls", "Wikipedia", "MedText", "MedCorp"
        db_dir: Directory to store corpus and indexes (default: "./corpus")
        cache: Whether to cache the entire corpus in memory for faster retrieval
        HNSW: Whether to use HNSW indexing for faster approximate search
        verbose: Whether to print progress messages
    """

    def __init__(
        self,
        retriever_name="MedCPT",
        corpus_name="Textbooks",
        db_dir="./corpus",
        cache=False,
        HNSW=False,
        verbose=True
    ):
        """Initialize the MedRAG Retriever."""
        self.retriever_name = retriever_name
        self.corpus_name = corpus_name
        self.db_dir = db_dir
        self.cache = cache
        self.HNSW = HNSW
        self.verbose = verbose

        if verbose:
            print(f"Initializing MedRAG Retriever...")
            print(f"  Retriever: {retriever_name}")
            print(f"  Corpus: {corpus_name}")
            print(f"  Cache: {cache}")
            print(f"  HNSW: {HNSW}")

        # Initialize the retrieval system using existing code
        self.retrieval_system = RetrievalSystem(
            retriever_name=retriever_name,
            corpus_name=corpus_name,
            db_dir=db_dir,
            cache=cache,
            HNSW=HNSW
        )

        if verbose:
            print("Initialization complete!")

    def search(self, query, k=32, rrf_k=100):
        """
        Search for relevant medical documents.

        Args:
            query: Search query string
            k: Number of documents to return
            rrf_k: RRF parameter for score fusion (only used with RRF retrievers)

        Returns:
            documents: List of document dictionaries with 'id', 'title', 'content'
            scores: List of relevance scores for each document
        """
        if self.verbose:
            print(f"\nSearching for: '{query}'")
            print(f"Retrieving top {k} documents...")

        documents, scores = self.retrieval_system.retrieve(query, k=k, rrf_k=rrf_k)

        if self.verbose:
            print(f"Found {len(documents)} documents")

        return documents, scores

    def batch_search(self, queries, k=32, rrf_k=100):
        """
        Search for multiple queries in batch.

        Args:
            queries: List of query strings
            k: Number of documents to return per query
            rrf_k: RRF parameter for score fusion

        Returns:
            results: List of (documents, scores) tuples for each query
        """
        if self.verbose:
            print(f"\nBatch search for {len(queries)} queries...")

        results = []
        for i, query in enumerate(queries):
            if self.verbose:
                print(f"  [{i+1}/{len(queries)}] {query}")
            docs, scores = self.search(query, k=k, rrf_k=rrf_k)
            results.append((docs, scores))

        return results

    def get_info(self):
        """Get information about the current retriever configuration."""
        retriever_info = get_retriever_info(self.retriever_name)
        corpus_info = get_corpus_info(self.corpus_name)

        return {
            "retriever": {
                "name": self.retriever_name,
                "info": retriever_info
            },
            "corpus": {
                "name": self.corpus_name,
                "info": corpus_info
            },
            "settings": {
                "db_dir": self.db_dir,
                "cache": self.cache,
                "HNSW": self.HNSW
            }
        }

    def print_results(self, documents, scores, max_content_length=200):
        """
        Print search results in a formatted way.

        Args:
            documents: List of document dictionaries
            scores: List of relevance scores
            max_content_length: Maximum length of content to display
        """
        print(f"\n{'='*80}")
        print(f"Search Results ({len(documents)} documents)")
        print('='*80)

        for i, (doc, score) in enumerate(zip(documents, scores)):
            print(f"\n[{i+1}] Score: {score:.4f}")
            print(f"Title: {doc['title']}")
            print(f"ID: {doc.get('id', 'N/A')}")
            content = doc['content'][:max_content_length]
            if len(doc['content']) > max_content_length:
                content += "..."
            print(f"Content: {content}")
            print('-'*80)

    def save_results(self, query, documents, scores, output_path):
        """
        Save search results to a JSON file.

        Args:
            query: The search query
            documents: List of document dictionaries
            scores: List of relevance scores
            output_path: Path to save the JSON file
        """
        import json

        result = {
            "query": query,
            "retriever": self.retriever_name,
            "corpus": self.corpus_name,
            "num_results": len(documents),
            "results": [
                {
                    "rank": i + 1,
                    "score": float(score),
                    "document": doc
                }
                for i, (doc, score) in enumerate(zip(documents, scores))
            ]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print(f"\nResults saved to {output_path}")

    @classmethod
    def from_preset(cls, preset_name, **kwargs):
        """
        Create a retriever from a preset configuration.

        Args:
            preset_name: Name of the preset ("fast", "balanced", "accurate")
            **kwargs: Additional arguments to override preset settings

        Returns:
            MedRAGRetriever instance
        """
        config = get_preset_config(preset_name)
        if config is None:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list_presets()}")

        config.update(kwargs)
        return cls(**config)
