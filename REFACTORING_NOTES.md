# MedRAG Retrieval System Refactoring

## Overview

This document describes the refactoring performed to optimize MedRAG retrieval system initialization across the multi-agent debate system.

## Changes Made

### 1. Moved MedRAG Retriever Package

**Before:**
```
/Hierarchical-Debate-MAS/
├── MedRAG_Retriever/
│   └── medrag_retriever/
│       ├── __init__.py
│       ├── core.py
│       └── config.py
└── tools/
    └── medrag_search.py
```

**After:**
```
/Hierarchical-Debate-MAS/
└── tools/
    ├── medrag_retriever/  (moved here)
    │   ├── __init__.py
    │   ├── core.py
    │   └── config.py
    └── medrag_search.py
```

**Reason:** Consolidates all tool-related code in one location for better organization.

### 2. Eliminated Global Singleton Pattern

**Before (tools/medrag_search.py):**
```python
# Global singleton
_retrieval_system = None

def _get_retrieval_system():
    global _retrieval_system
    if _retrieval_system is None:
        _retrieval_system = RetrievalSystem(...)
    return _retrieval_system

def medrag_search_tool(query, k=5):
    retrieval_system = _get_retrieval_system()
    # ... use retrieval_system
```

**After (tools/medrag_search.py):**
```python
def create_medrag_search_tool(retrieval_system: RetrievalSystem):
    """Factory function that creates a tool with a shared retrieval system."""
    def medrag_search_tool(query, k=5):
        # Use the passed-in retrieval_system
        documents, scores = retrieval_system.retrieve(...)
        # ... format results
    return medrag_search_tool
```

**Reason:**
- Removes hidden global state
- Makes dependencies explicit
- Allows better control over initialization timing
- Enables dependency injection for testing

### 3. Initialize Once in Main

**main.py changes:**
```python
class MultiAgentDebateSystem:
    def __init__(
        self,
        # ... other params
        retriever_name: str = "MedCPT",
        corpus_name: str = "Textbooks",
        db_dir: str = "/data/multi-agent_snuh/MedRAG/corpus"
    ):
        # Initialize ONCE at system startup
        self.retrieval_system = RetrievalSystem(
            retriever_name=retriever_name,
            corpus_name=corpus_name,
            db_dir=db_dir,
            HNSW=False,
            cache=False
        )

        # Pass to Phase 1 orchestrator
        self.phase1 = Phase1Orchestrator(
            model_client=self.model_client,
            work_dir=work_dir,
            logger=self.logger,
            retrieval_system=self.retrieval_system  # NEW
        )
```

**Benefits:**
- Single initialization at startup (faster, predictable)
- Configuration centralized in main.py
- Easy to customize retriever settings
- Clear lifecycle management

### 4. Pass Through Orchestration Layers

**Phase1Orchestrator (orchestration/phase1_parallel.py):**
```python
class Phase1Orchestrator:
    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        work_dir: Path = CODING_DIR,
        logger: Optional[TranscriptLogger] = None,
        retrieval_system: Optional[RetrievalSystem] = None  # NEW
    ):
        self.retrieval_system = retrieval_system

        # Pass to all groups
        self.groups = [
            GroupTeam(
                group_name=name,
                model_client=model_client,
                work_dir=work_dir,
                retrieval_system=retrieval_system  # NEW
            )
            for name in GROUP_NAMES
        ]
```

### 5. Create Tool Instances Per Group

**GroupTeam (teams/group_team.py):**
```python
class GroupTeam:
    def __init__(
        self,
        group_name: str,
        model_client: OpenAIChatCompletionClient,
        work_dir: Path,
        retrieval_system: Optional[RetrievalSystem] = None  # NEW
    ):
        self.retrieval_system = retrieval_system

        # Create tool function with shared retrieval system
        if self.retrieval_system is not None:
            self.medrag_search_tool = create_medrag_search_tool(
                self.retrieval_system
            )
        else:
            # Fallback if no retrieval system provided
            self.medrag_search_tool = lambda query, k=5: "Error: Not initialized"

        # ... create agents

        # Researcher uses the group's tool instance
        self.researcher = AssistantAgent(
            name=f"{self.group_name}Researcher",
            tools=[self.medrag_search_tool, web_search_tool],  # NEW
            # ...
        )
```

**Key Points:**
- Each group gets its own tool function
- All tool functions share the SAME underlying RetrievalSystem
- No redundant initialization
- Clean separation of concerns

## Architecture Diagram

```
main.py
  └─ MultiAgentDebateSystem.__init__()
       │
       ├─ Initialize RetrievalSystem (ONCE)
       │   └─ self.retrieval_system = RetrievalSystem(...)
       │
       └─ Pass to Phase1Orchestrator
            │
            └─ Phase1Orchestrator.__init__(retrieval_system)
                 │
                 ├─ Group 1 (GroupTeam)
                 │   ├─ create_medrag_search_tool(retrieval_system) → tool1
                 │   └─ Researcher uses tool1
                 │
                 ├─ Group 2 (GroupTeam)
                 │   ├─ create_medrag_search_tool(retrieval_system) → tool2
                 │   └─ Researcher uses tool2
                 │
                 └─ Group 3 (GroupTeam)
                     ├─ create_medrag_search_tool(retrieval_system) → tool3
                     └─ Researcher uses tool3

Note: tool1, tool2, tool3 are different functions but share the SAME RetrievalSystem instance
```

## Performance Improvements

### Before:
- **Lazy initialization:** First call to any researcher tool triggers initialization
- **Unpredictable timing:** Could happen during critical task execution
- **Hidden complexity:** Initialization happened inside tool function

### After:
- **Eager initialization:** Happens once at system startup
- **Predictable timing:** All setup done before task execution begins
- **Transparent:** Clear initialization in main.py
- **Shared resources:** All researchers use the same loaded corpus/embeddings

## Memory and Resource Benefits

1. **Single Corpus Load:** Corpus loaded once, not per-group
2. **Single Index Load:** FAISS/embeddings loaded once
3. **Shared Memory:** All researchers access same data structures
4. **No Redundant I/O:** No duplicate file reads or model loading

## Usage Example

```python
from main import MultiAgentDebateSystem

# Create system (this initializes MedRAG once)
system = MultiAgentDebateSystem(
    retriever_name="MedCPT",      # Configurable!
    corpus_name="Textbooks",       # Configurable!
    db_dir="/path/to/corpus"       # Configurable!
)

# Run task (all researchers share the initialized retrieval system)
result = await system.run(task="Analyze asthma phenotypes")
```

## Testing

Run the test script to verify the refactoring:

```bash
cd /home/hyesung/multi-agent/ex_version/Hierarchical-Debate-MAS
python test_retrieval.py
```

This will:
1. Initialize a single RetrievalSystem
2. Create multiple tool instances
3. Verify all instances share the same underlying system
4. Test retrieval with sample queries

## Migration Notes

If you have existing code that imports `medrag_search_tool` directly:

**Old import (no longer works):**
```python
from tools import medrag_search_tool
```

**New pattern:**
```python
from tools import create_medrag_search_tool, RetrievalSystem

# Initialize system
retrieval_system = RetrievalSystem(...)

# Create tool
medrag_search_tool = create_medrag_search_tool(retrieval_system)

# Use tool
result = medrag_search_tool(query="...", k=5)
```

## Future Improvements

Potential enhancements:
1. **Multiple Corpora:** Different groups could use different corpora
2. **Retriever Pool:** Support multiple retriever types simultaneously
3. **Caching Strategy:** Add optional result caching per-session
4. **Async Retrieval:** Make retrieval operations async for better concurrency
5. **Metrics:** Add retrieval performance tracking and logging
