---
name: nova-memory
description: >-
  Operational procedures for Nova's persistent memory, knowledge graphs, local vector storage (RAG), historical conversation indexing, and context window optimization.
---

# Nova Memory Subsystem Skill

Use this skill when implementing, querying, optimizing, or auditing memory storage, vector databases, knowledge graphs, RAG pipelines, or session persistence.

## Subsystem Architecture Overview

Memory components live in `apps/backend/app/memory/`, `apps/backend/app/vector_memory/`, `apps/backend/app/knowledge_graph/`, and `apps/backend/app/rag/`:
- `memory/memory_manager.py`: Central memory store managing short-term, working, and long-term memory.
- `vector_memory/vector_store.py`: Local vector embedding index (ChromaDB / FAISS / SQLite-vss).
- `knowledge_graph/graph_engine.py`: Entity and relationship graph engine.
- `rag/rag_pipeline.py`: Context retrieval and document augmentation pipeline.

## Core Operations & Guidelines

### 1. Zero-Cost Local Vector Embeddings
- Use local embedding models (e.g. `all-MiniLM-L6-v2`, `bge-small-en`) running via sentence-transformers or local Ollama embeddings.
- Vector indices must be persisted to disk under local data paths (`data/memory/`, `data/vectors/`).

### 2. Context Window & Memory Tiering
- **Short-Term Memory**: Conversation history buffer managed per session.
- **Working Memory**: Active plan state, active document context, user preferences.
- **Long-Term Memory**: Semantic vector index + Knowledge Graph entities.

### 3. Memory Retrieval Procedures
1. Query vector index for relevant semantic matches.
2. Query knowledge graph for connected entity relationships.
3. Merge, deduplicate, and rank retrieved snippets before injecting into model context window.

### 4. Verification & Testing
- Run memory unit test suite:
  ```powershell
  pytest tests/unit/test_memory.py
  ```
- Test workspace memory integration:
  ```powershell
  python test_workspace_manual.py
  ```
