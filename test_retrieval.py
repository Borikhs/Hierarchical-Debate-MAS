"""
Test script to verify MedRAG retrieval system initialization.
"""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools import RetrievalSystem, create_medrag_search_tool

def test_retrieval_system():
    """Test that retrieval system can be initialized and used."""
    print("="*60)
    print("Testing MedRAG Retrieval System Initialization")
    print("="*60)

    # Initialize retrieval system
    print("\n1. Initializing RetrievalSystem...")
    retrieval_system = RetrievalSystem(
        retriever_name="MedCPT",
        corpus_name="Textbooks",
        db_dir="/data/multi-agent_snuh/MedRAG/corpus",
        HNSW=False,
        cache=False
    )
    print("   ✓ RetrievalSystem initialized successfully")

    # Create tool function
    print("\n2. Creating medrag_search_tool...")
    medrag_search_tool = create_medrag_search_tool(retrieval_system)
    print("   ✓ Tool function created successfully")

    # Test retrieval
    print("\n3. Testing retrieval with a sample query...")
    query = "What is asthma?"
    result = medrag_search_tool(query=query, k=2)
    print(f"   ✓ Retrieved results for query: '{query}'")
    print(f"\n   Result preview (first 500 chars):")
    print(f"   {'-'*56}")
    print(f"   {result[:500]}...")
    print(f"   {'-'*56}")

    print("\n4. Testing with multiple tool instances...")
    # Simulate creating multiple groups with same retrieval system
    tool1 = create_medrag_search_tool(retrieval_system)
    tool2 = create_medrag_search_tool(retrieval_system)
    tool3 = create_medrag_search_tool(retrieval_system)

    result1 = tool1(query="diabetes", k=1)
    result2 = tool2(query="hypertension", k=1)
    result3 = tool3(query="pneumonia", k=1)

    print("   ✓ Tool 1 (diabetes): Retrieved successfully")
    print("   ✓ Tool 2 (hypertension): Retrieved successfully")
    print("   ✓ Tool 3 (pneumonia): Retrieved successfully")

    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    print("\nThe shared retrieval system is working correctly.")
    print("All tool instances use the same underlying RetrievalSystem.")

if __name__ == "__main__":
    try:
        test_retrieval_system()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
