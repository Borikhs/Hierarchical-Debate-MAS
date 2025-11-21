"""
MedRAG search tool for agents to retrieve medical information.

This tool provides access to medical literature from various sources:
- Textbooks: Medical textbooks (~18,000 documents)
- StatPearls: Clinical guidelines (~3,000+ documents)
- PubMed: Research abstracts (2M+ documents)
- Wikipedia: Medical articles (~20,000+ documents)
"""
from typing import Annotated


# Module-level shared retrieval system instance
_retrieval_system = None


def initialize_medrag_retriever(retrieval_system):
    """
    Initialize the shared MedRAG retrieval system.

    This should be called once at startup to set up the retrieval system
    that will be shared across all medrag_search_tool calls.

    Args:
        retrieval_system: RetrievalSystem instance to use for searches

    Example:
        >>> from .medrag_retriever import RetrievalSystem
        >>> system = RetrievalSystem(retriever_name="MedCPT", corpus_name="Textbooks")
        >>> initialize_medrag_retriever(system)
    """
    global _retrieval_system
    _retrieval_system = retrieval_system


def medrag_search_tool(
    query: Annotated[str, "Medical question or query to search for"],
    k: Annotated[int, "Number of documents to retrieve (default: 5)"] = 5
) -> Annotated[str, "Retrieved medical information from MedRAG corpus"]:
    """
    Search medical literature using MedRAG retrieval system.

    This tool searches through medical textbooks, guidelines, and literature
    to find relevant information for medical questions.

    Args:
        query: The medical question or query to search for
        k: Number of relevant documents to retrieve (1-32, default: 5)

    Returns:
        Formatted string with retrieved medical information

    Example:
        medrag_search_tool("What is the treatment for type 2 diabetes?", k=3)
    """
    try:
        # Check if retrieval system is initialized
        if _retrieval_system is None:
            return "Error: MedRAG retrieval system not initialized. Call initialize_medrag_retriever() first."

        # Validate parameters
        if not query or not query.strip():
            return "Error: Query cannot be empty"

        # Clamp k to reasonable range
        k = max(1, min(k, 32))

        # Retrieve documents using the shared retrieval system
        documents, scores = _retrieval_system.retrieve(
            question=query,
            k=k,
            rrf_k=100
        )

        if not documents:
            return f"No relevant medical information found for: '{query}'"

        # Format results
        result_parts = [
            f"Medical Information Search Results for: \"{query}\"",
            f"Retrieved {len(documents)} relevant document(s) from medical literature:",
            ""
        ]

        for idx, (doc, score) in enumerate(zip(documents, scores), 1):
            title = doc.get('title', 'Unknown Source')
            content = doc.get('content', 'No content available')
            doc_id = doc.get('id', 'Unknown ID')

            result_parts.append(f"--- Document {idx} (Relevance Score: {score:.4f}) ---")
            result_parts.append(f"Source: {title}")
            result_parts.append(f"ID: {doc_id}")
            result_parts.append(f"Content:\n{content}")
            result_parts.append("")

        result = "\n".join(result_parts)

        # Limit output length to avoid overwhelming the agent
        max_length = 8000  # characters
        if len(result) > max_length:
            result = result[:max_length] + f"\n\n[Output truncated - showing {max_length} of {len(result)} characters]"

        return result

    except Exception as e:
        return f"Error during MedRAG search: {str(e)}"


def create_medrag_search_tool(retrieval_system):
    """
    Deprecated: Use initialize_medrag_retriever() instead.

    This function is kept for backward compatibility.
    It initializes the global retrieval system and returns the search tool function.

    Args:
        retrieval_system: RetrievalSystem instance

    Returns:
        medrag_search_tool function
    """
    initialize_medrag_retriever(retrieval_system)
    return medrag_search_tool
