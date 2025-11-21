"""Tools module."""
from .web_search import web_search_tool
from .medrag_search import (
    medrag_search_tool,
    initialize_medrag_retriever,
    create_medrag_search_tool  # Backward compatibility
)
from .medrag_retriever import RetrievalSystem

__all__ = [
    "web_search_tool",
    "medrag_search_tool",
    "initialize_medrag_retriever",
    "create_medrag_search_tool",
    "RetrievalSystem"
]
