"""
MedRAG Retriever Configuration

This module contains configuration settings for the MedRAG Retriever package.
Based on the original MedRAG project but focused on retrieval functionality only.
"""

# Default Configuration
DEFAULT_CONFIG = {
    "retriever_name": "MedCPT",
    "corpus_name": "Textbooks",
    "db_dir": "/data/multi-agent_snuh/MedRAG/corpus",
    "cache": False,
    "HNSW": False,
}

# Supported Retriever Options
RETRIEVER_OPTIONS = {
    "BM25": {
        "description": "Lexical-based retrieval using BM25 algorithm",
        "models": ["bm25"],
        "recommended_for": "Keyword-based search, fast retrieval"
    },
    "Contriever": {
        "description": "General domain dense retrieval",
        "models": ["facebook/contriever"],
        "recommended_for": "General purpose semantic search"
    },
    "SPECTER": {
        "description": "Scientific paper specialized retrieval",
        "models": ["allenai/specter"],
        "recommended_for": "Scientific literature search"
    },
    "MedCPT": {
        "description": "Medical domain specialized retrieval (Recommended)",
        "models": ["ncbi/MedCPT-Query-Encoder"],
        "recommended_for": "Medical question answering, clinical queries"
    },
    "RRF-2": {
        "description": "Hybrid retrieval combining BM25 and MedCPT",
        "models": ["bm25", "ncbi/MedCPT-Query-Encoder"],
        "recommended_for": "Best performance, combines lexical and semantic"
    },
    "RRF-4": {
        "description": "Ensemble of 4 retrievers (highest performance)",
        "models": ["bm25", "facebook/contriever", "allenai/specter", "ncbi/MedCPT-Query-Encoder"],
        "recommended_for": "Maximum accuracy, slower but comprehensive"
    }
}

# Supported Corpus Options
CORPUS_OPTIONS = {
    "Textbooks": {
        "description": "Medical textbooks corpus",
        "documents": "~18,000",
        "size": "~50 MB",
        "characteristics": "Systematic, educational content"
    },
    "PubMed": {
        "description": "PubMed abstracts corpus",
        "documents": "~2,000,000+",
        "size": "~15 GB",
        "characteristics": "Latest research, professional content"
    },
    "StatPearls": {
        "description": "StatPearls clinical guidelines",
        "documents": "~3,000+",
        "size": "~20 MB",
        "characteristics": "Clinical guidelines, evidence-based"
    },
    "Wikipedia": {
        "description": "Wikipedia medical articles",
        "documents": "~20,000+",
        "size": "~200 MB",
        "characteristics": "General knowledge, accessible"
    },
    "MedText": {
        "description": "Combined Textbooks + StatPearls",
        "documents": "~21,000+",
        "size": "~70 MB",
        "characteristics": "Comprehensive educational + clinical"
    },
    "MedCorp": {
        "description": "Full corpus (all sources combined)",
        "documents": "~2,040,000+",
        "size": "~15.3 GB",
        "characteristics": "Most comprehensive, requires large storage"
    }
}

# System Requirements
SYSTEM_REQUIREMENTS = {
    "disk_space": {
        "Textbooks": "~160 MB",
        "PubMed": "~27 GB",
        "StatPearls": "~40 MB",
        "Wikipedia": "~500 MB",
        "MedCorp": "~30 GB"
    },
    "memory": {
        "cache_disabled": "~2 GB",
        "cache_enabled_textbooks": "~2 GB",
        "cache_enabled_medcorp": "~20 GB"
    },
    "gpu": {
        "required": False,
        "recommended": True,
        "benefit": "10-50x faster embedding generation"
    }
}

# Performance Settings
PERFORMANCE_PRESETS = {
    "fast": {
        "description": "Fast retrieval, lower memory usage",
        "cache": False,
        "HNSW": True,
        "corpus_name": "Textbooks"
    },
    "balanced": {
        "description": "Balanced performance and accuracy",
        "cache": True,
        "HNSW": True,
        "corpus_name": "MedText"
    },
    "accurate": {
        "description": "Highest accuracy, more resources",
        "cache": True,
        "HNSW": False,
        "corpus_name": "MedCorp"
    }
}

def get_retriever_info(retriever_name):
    """Get information about a specific retriever."""
    return RETRIEVER_OPTIONS.get(retriever_name, None)

def get_corpus_info(corpus_name):
    """Get information about a specific corpus."""
    return CORPUS_OPTIONS.get(corpus_name, None)

def get_preset_config(preset_name):
    """Get a preset configuration."""
    preset = PERFORMANCE_PRESETS.get(preset_name, None)
    if preset:
        config = DEFAULT_CONFIG.copy()
        config.update(preset)
        return config
    return None

def list_retrievers():
    """List all available retrievers."""
    return list(RETRIEVER_OPTIONS.keys())

def list_corpora():
    """List all available corpora."""
    return list(CORPUS_OPTIONS.keys())

def list_presets():
    """List all available presets."""
    return list(PERFORMANCE_PRESETS.keys())
