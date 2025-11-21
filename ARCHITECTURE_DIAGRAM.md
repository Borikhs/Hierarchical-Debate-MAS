# Architecture: MedRAG Retrieval System Flow

## Before Refactoring (Old Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│ main.py                                                      │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ MultiAgentDebateSystem                              │    │
│ │  - No retrieval system initialization               │    │
│ └─────────────────────────────────────────────────────┘    │
│                     │                                        │
│                     ▼                                        │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Phase1Orchestrator                                  │    │
│ │  - No retrieval system                              │    │
│ └─────────────────────────────────────────────────────┘    │
│           │              │              │                    │
│           ▼              ▼              ▼                    │
│    ┌──────────┐   ┌──────────┐   ┌──────────┐             │
│    │ Group 1  │   │ Group 2  │   │ Group 3  │             │
│    └──────────┘   └──────────┘   └──────────┘             │
│           │              │              │                    │
└───────────┼──────────────┼──────────────┼────────────────────┘
            │              │              │
            ▼              ▼              ▼
     ┌───────────┐  ┌───────────┐  ┌───────────┐
     │Researcher1│  │Researcher2│  │Researcher3│
     └───────────┘  └───────────┘  └───────────┘
            │              │              │
            │ First call   │ First call   │ First call
            ▼              ▼              ▼
    ┌────────────────────────────────────────────┐
    │ tools/medrag_search.py                     │
    │                                            │
    │  _retrieval_system = None  (GLOBAL)       │ ← Hidden global state!
    │                                            │
    │  def _get_retrieval_system():             │
    │      global _retrieval_system             │
    │      if _retrieval_system is None:        │ ← Lazy init on first use
    │          _retrieval_system = ...          │ ← UNPREDICTABLE TIMING
    │      return _retrieval_system             │
    │                                            │
    │  def medrag_search_tool(query, k):        │
    │      system = _get_retrieval_system()     │ ← Implicitly uses global
    │      return system.retrieve(...)          │
    └────────────────────────────────────────────┘
```

### Problems with Old Architecture:
1. ❌ **Unpredictable timing**: Initialization happens on first researcher's first query
2. ❌ **Hidden state**: Global variable not visible in call chain
3. ❌ **Not configurable**: Settings hardcoded in `medrag_search.py`
4. ❌ **Hard to test**: Can't inject mock retrieval system
5. ❌ **Tight coupling**: Tool has hidden dependency on global state

---

## After Refactoring (New Architecture)

```
┌─────────────────────────────────────────────────────────────────────┐
│ main.py                                                              │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ MultiAgentDebateSystem.__init__(...)                           │ │
│ │                                                                 │ │
│ │  ┌──────────────────────────────────────────────────────────┐ │ │
│ │  │ 1. Initialize RetrievalSystem ONCE at startup            │ │ │
│ │  │                                                           │ │ │
│ │  │  self.retrieval_system = RetrievalSystem(                │ │ │
│ │  │      retriever_name="MedCPT",     ← Configurable!        │ │ │
│ │  │      corpus_name="Textbooks",     ← Configurable!        │ │ │
│ │  │      db_dir="/path/to/corpus"     ← Configurable!        │ │ │
│ │  │  )                                                        │ │ │
│ │  │                                                           │ │ │
│ │  │  ✓ Loads corpus from disk                                │ │ │
│ │  │  ✓ Loads embeddings/index                                │ │ │
│ │  │  ✓ Predictable timing                                    │ │ │
│ │  └──────────────────────────────────────────────────────────┘ │ │
│ │                                                                 │ │
│ │  self.phase1 = Phase1Orchestrator(                             │ │
│ │      ...,                                                       │ │
│ │      retrieval_system=self.retrieval_system  ← Pass down       │ │
│ │  )                                                              │ │
│ └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ orchestration/phase1_parallel.py                                    │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Phase1Orchestrator.__init__(..., retrieval_system)             │ │
│ │                                                                 │ │
│ │  self.retrieval_system = retrieval_system  ← Store reference   │ │
│ │                                                                 │ │
│ │  self.groups = [                                               │ │
│ │      GroupTeam(..., retrieval_system=retrieval_system),  ←─┐   │ │
│ │      GroupTeam(..., retrieval_system=retrieval_system),  ←─┼─┐ │ │
│ │      GroupTeam(..., retrieval_system=retrieval_system)   ←─┼─┼─│─┐
│ │  ]                                                             │ │ │
│ └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                      │                  │                  │
                      ▼                  ▼                  ▼
      ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
      │ teams/group_team.py│  │ teams/group_team.py│  │ teams/group_team.py│
      │ ┌───────────────┐ │  │ ┌───────────────┐ │  │ ┌───────────────┐ │
      │ │ GroupTeam 1   │ │  │ │ GroupTeam 2   │ │  │ │ GroupTeam 3   │ │
      │ │               │ │  │ │               │ │  │ │               │ │
      │ │ ┌───────────┐ │ │  │ │ ┌───────────┐ │ │  │ │ ┌───────────┐ │ │
      │ │ │ Create    │ │ │  │ │ │ Create    │ │ │  │ │ │ Create    │ │ │
      │ │ │ tool with │ │ │  │ │ │ tool with │ │ │  │ │ │ tool with │ │ │
      │ │ │ shared    │ │ │  │ │ │ shared    │ │ │  │ │ │ shared    │ │ │
      │ │ │ system:   │ │ │  │ │ │ system:   │ │ │  │ │ │ system:   │ │ │
      │ │ │           │ │ │  │ │ │           │ │ │  │ │ │           │ │ │
      │ │ │ self.     │ │ │  │ │ │ self.     │ │ │  │ │ │ self.     │ │ │
      │ │ │ medrag_   │ │ │  │ │ │ medrag_   │ │ │  │ │ │ medrag_   │ │ │
      │ │ │ search_   │ │ │  │ │ │ search_   │ │ │  │ │ │ search_   │ │ │
      │ │ │ tool = ───┼─┼─┼──┼─┼─┼─tool = ───┼─┼─┼──┼─┼─┼─tool = ───┼─┼─┼──┐
      │ │ │ create_   │ │ │  │ │ │ create_   │ │ │  │ │ │ create_   │ │ │  │
      │ │ │ medrag_   │ │ │  │ │ │ medrag_   │ │ │  │ │ │ medrag_   │ │ │  │
      │ │ │ search_   │ │ │  │ │ │ search_   │ │ │  │ │ │ search_   │ │ │  │
      │ │ │ tool(     │ │ │  │ │ │ tool(     │ │ │  │ │ │ tool(     │ │ │  │
      │ │ │ retrieval_│ │ │  │ │ │ retrieval_│ │ │  │ │ │ retrieval_│ │ │  │
      │ │ │ system    │ │ │  │ │ │ system    │ │ │  │ │ │ system    │ │ │  │
      │ │ │ )         │ │ │  │ │ │ )         │ │ │  │ │ │ )         │ │ │  │
      │ │ └───────────┘ │ │  │ │ └───────────┘ │ │  │ │ └───────────┘ │ │  │
      │ │               │ │  │ │               │ │  │ │               │ │  │
      │ │ Researcher1   │ │  │ │ Researcher2   │ │  │ │ Researcher3   │ │  │
      │ │ uses this tool│ │  │ │ uses this tool│ │  │ │ uses this tool│ │  │
      │ └───────────────┘ │  │ └───────────────┘ │  │ └───────────────┘ │  │
      └───────────────────┘  └───────────────────┘  └───────────────────┘  │
                                                                            │
                                                                            │
                   ┌────────────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ tools/medrag_search.py                                               │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ def create_medrag_search_tool(retrieval_system):               │ │
│  │     """Factory: Creates tool with dependency injection"""      │ │
│  │                                                                 │ │
│  │     def medrag_search_tool(query, k=5):                        │ │
│  │         # Uses the injected retrieval_system                   │ │
│  │         documents, scores = retrieval_system.retrieve(...)     │ │
│  │         return format_results(documents, scores)               │ │
│  │                                                                 │ │
│  │     return medrag_search_tool                                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ✓ No global state                                                   │
│  ✓ Explicit dependency                                               │
│  ✓ Testable (can inject mock)                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Benefits of New Architecture:

1. ✅ **Predictable**: Initialization happens at system startup
2. ✅ **Explicit**: Retrieval system passed through call chain
3. ✅ **Configurable**: Settings in `main.py` constructor
4. ✅ **Testable**: Easy to inject mock for testing
5. ✅ **Efficient**: Single initialization, shared by all researchers
6. ✅ **Clear ownership**: `MultiAgentDebateSystem` owns the resource

---

## Memory Layout

### Before (Lazy Global Singleton):
```
First researcher query triggers:
┌──────────────────────────────┐
│ Global: _retrieval_system    │
│  ├─ Corpus data (in memory)  │
│  ├─ Embeddings (in memory)   │
│  └─ FAISS index (in memory)  │
└──────────────────────────────┘
         ▲
         │ (implicitly used by all)
         │
    All researchers
```

### After (Explicit Shared Instance):
```
At startup:
┌──────────────────────────────────────────────┐
│ MultiAgentDebateSystem                       │
│  └─ self.retrieval_system                    │
│       ├─ Corpus data (in memory)             │
│       ├─ Embeddings (in memory)              │
│       └─ FAISS index (in memory)             │
└──────────────────────────────────────────────┘
         │
         ├─ passed to ─→ Phase1Orchestrator
         │                    │
         │                    ├─ passed to ─→ GroupTeam 1
         │                    │                    │
         │                    │                    └─→ tool1(uses retrieval_system)
         │                    │
         │                    ├─ passed to ─→ GroupTeam 2
         │                    │                    │
         │                    │                    └─→ tool2(uses retrieval_system)
         │                    │
         │                    └─ passed to ─→ GroupTeam 3
         │                                         │
         │                                         └─→ tool3(uses retrieval_system)
         │
    (Same instance shared by all tools)
```

**Result**: Single copy in memory, explicitly shared, no hidden magic!

---

## Execution Flow Comparison

### Before:
```
1. main.py starts
2. Creates MultiAgentDebateSystem
3. Creates Phase1Orchestrator
4. Creates 3 GroupTeams
5. Creates 3 Researchers
6. Run task
7. Researcher 1 calls medrag_search_tool
   → Triggers _get_retrieval_system()
   → LOADS CORPUS (slow, unpredictable)  ← PROBLEM!
8. Researcher 2 calls medrag_search_tool
   → Uses global _retrieval_system
9. Researcher 3 calls medrag_search_tool
   → Uses global _retrieval_system
```

### After:
```
1. main.py starts
2. Creates MultiAgentDebateSystem
   → LOADS CORPUS (predictable, at startup)  ← BETTER!
3. Creates Phase1Orchestrator (passes retrieval_system)
4. Creates 3 GroupTeams (passes retrieval_system)
5. Each GroupTeam creates tool with retrieval_system
6. Creates 3 Researchers (with configured tools)
7. Run task
8. Researcher 1 calls tool → retrieval_system.retrieve() (fast)
9. Researcher 2 calls tool → retrieval_system.retrieve() (fast)
10. Researcher 3 calls tool → retrieval_system.retrieve() (fast)
```

**Result**: Initialization happens once, at a predictable time, before any work begins!
