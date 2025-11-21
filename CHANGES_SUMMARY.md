# Refactoring Summary: Shared MedRAG Retrieval System

## What Changed

This refactoring transforms the MedRAG retrieval system from a lazy-initialized global singleton to a properly dependency-injected shared resource initialized once in `main.py`.

## Files Modified

### 1. **tools/medrag_search.py**
- ❌ Removed global `_retrieval_system` variable
- ❌ Removed `_get_retrieval_system()` lazy initializer
- ❌ Removed sys.path manipulation
- ✅ Added `create_medrag_search_tool(retrieval_system)` factory function
- ✅ Changed import from `MedRAG_Retriever` to relative import from `tools.medrag_retriever`

**Key change:**
```python
# OLD: Global singleton pattern
_retrieval_system = None
def medrag_search_tool(query, k=5):
    retrieval_system = _get_retrieval_system()
    ...

# NEW: Factory function with dependency injection
def create_medrag_search_tool(retrieval_system):
    def medrag_search_tool(query, k=5):
        documents, scores = retrieval_system.retrieve(...)
        ...
    return medrag_search_tool
```

### 2. **tools/__init__.py**
```python
# OLD
from .medrag_search import medrag_search_tool, medrag_search_simple

# NEW
from .medrag_search import create_medrag_search_tool
from .medrag_retriever import RetrievalSystem
```

### 3. **main.py**
- ✅ Added import: `from tools import RetrievalSystem`
- ✅ Added initialization parameters: `retriever_name`, `corpus_name`, `db_dir`
- ✅ Initialize `RetrievalSystem` once in `__init__`
- ✅ Pass `retrieval_system` to `Phase1Orchestrator`

**Key addition:**
```python
def __init__(self, ..., retriever_name="MedCPT", corpus_name="Textbooks", db_dir="..."):
    # Initialize ONCE at startup
    self.retrieval_system = RetrievalSystem(
        retriever_name=retriever_name,
        corpus_name=corpus_name,
        db_dir=db_dir,
        HNSW=False,
        cache=False
    )

    # Pass to orchestrator
    self.phase1 = Phase1Orchestrator(..., retrieval_system=self.retrieval_system)
```

### 4. **orchestration/phase1_parallel.py**
- ✅ Added import: `from tools import RetrievalSystem`
- ✅ Added `retrieval_system` parameter to `__init__`
- ✅ Pass `retrieval_system` to each `GroupTeam`

**Key change:**
```python
def __init__(self, ..., retrieval_system=None):
    self.retrieval_system = retrieval_system
    self.groups = [
        GroupTeam(..., retrieval_system=retrieval_system)  # Pass to groups
        for name in GROUP_NAMES
    ]
```

### 5. **teams/group_team.py**
- ✅ Updated import: `from tools import web_search_tool, create_medrag_search_tool, RetrievalSystem`
- ✅ Added `retrieval_system` parameter to `__init__`
- ✅ Create `self.medrag_search_tool` using factory function
- ✅ Use `self.medrag_search_tool` in researcher's tool list

**Key change:**
```python
def __init__(self, ..., retrieval_system=None):
    self.retrieval_system = retrieval_system

    # Create tool with shared retrieval system
    if self.retrieval_system is not None:
        self.medrag_search_tool = create_medrag_search_tool(self.retrieval_system)
    else:
        self.medrag_search_tool = lambda query, k=5: "Error: Not initialized"

    # Use in researcher
    self.researcher = AssistantAgent(
        ...,
        tools=[self.medrag_search_tool, web_search_tool]  # Use instance variable
    )
```

### 6. **tools/medrag_retriever/** (moved)
- 📁 Moved from `MedRAG_Retriever/medrag_retriever/` to `tools/medrag_retriever/`
- Files: `__init__.py`, `core.py`, `config.py`

## New Files Created

1. **test_retrieval.py** - Test script to verify the refactoring works correctly
2. **REFACTORING_NOTES.md** - Detailed documentation of the refactoring
3. **CHANGES_SUMMARY.md** - This file (quick reference)

## Directory Structure

```
Before:
/Hierarchical-Debate-MAS/
├── MedRAG_Retriever/
│   └── medrag_retriever/
└── tools/
    └── medrag_search.py (uses sys.path to import from MedRAG_Retriever)

After:
/Hierarchical-Debate-MAS/
└── tools/
    ├── medrag_retriever/  ← MOVED HERE
    │   ├── __init__.py
    │   ├── core.py
    │   └── config.py
    └── medrag_search.py (uses relative import)
```

## Benefits

### Performance
- ✅ Initialize corpus once (not lazily per first use)
- ✅ All 3 groups share the same loaded data
- ✅ Predictable startup time
- ✅ No redundant I/O or model loading

### Code Quality
- ✅ No global state
- ✅ Explicit dependencies
- ✅ Testable (can inject mock retrieval system)
- ✅ Clear initialization flow
- ✅ Configurable from main.py

### Maintainability
- ✅ Configuration centralized in main.py
- ✅ Easy to change retriever/corpus settings
- ✅ Clear ownership of resources
- ✅ Better error handling

## How to Use

### Basic Usage (same as before)
```python
system = MultiAgentDebateSystem()
result = await system.run(task="Your question here")
```

### Custom Configuration (NEW!)
```python
system = MultiAgentDebateSystem(
    retriever_name="RRF-4",        # Use ensemble retriever
    corpus_name="PubMed",          # Use PubMed instead of Textbooks
    db_dir="/custom/path/corpus"   # Custom corpus location
)
result = await system.run(task="Your question here")
```

## Testing

Run the test script:
```bash
cd /home/hyesung/multi-agent/ex_version/Hierarchical-Debate-MAS
python test_retrieval.py
```

Expected output:
```
============================================================
Testing MedRAG Retrieval System Initialization
============================================================

1. Initializing RetrievalSystem...
   ✓ RetrievalSystem initialized successfully

2. Creating medrag_search_tool...
   ✓ Tool function created successfully

3. Testing retrieval with a sample query...
   ✓ Retrieved results for query: 'What is asthma?'
   ...

4. Testing with multiple tool instances...
   ✓ Tool 1 (diabetes): Retrieved successfully
   ✓ Tool 2 (hypertension): Retrieved successfully
   ✓ Tool 3 (pneumonia): Retrieved successfully

============================================================
All tests passed! ✓
============================================================
```

## Backward Compatibility

⚠️ **Breaking Change:** Direct imports of `medrag_search_tool` no longer work.

If you have external code using the tool, update it:

```python
# OLD (no longer works)
from tools import medrag_search_tool
result = medrag_search_tool("query")

# NEW
from tools import create_medrag_search_tool, RetrievalSystem

retrieval_system = RetrievalSystem(...)
medrag_tool = create_medrag_search_tool(retrieval_system)
result = medrag_tool("query")
```

However, if you're using the system through `MultiAgentDebateSystem`, everything works transparently.

## Questions?

For detailed information, see [REFACTORING_NOTES.md](REFACTORING_NOTES.md).
