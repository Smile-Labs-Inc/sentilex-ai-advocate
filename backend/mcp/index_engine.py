import json
import os
import math
import hashlib
from collections import defaultdict
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class AntigravityIndex:
    """
    Implements the indexing and search logic for the Antigravity Pipeline.
    Manages documents, chunks, vectors, and entity graphs.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.documents = {}  # file_id -> doc_metadata
        self.chunks = {}     # chunk_id -> chunk_data
        self.vectors = {}    # chunk_id -> vector (list or np.array)
        self.graph = {       # Adjacency list for entity graph
            "nodes": {},     # id -> node_data
            "edges": []      # list of {source, target, relation}
        }
        self.inverted_index = defaultdict(list) # term -> list of chunk_ids
        self.faceted_index = defaultdict(lambda: defaultdict(list)) # field -> value -> list of ids
        
        self.index_dir = self.config.get("index_dir", "backend/data/index")
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)

    def add_document(self, doc: Dict[str, Any]):
        """Adds a document to the index."""
        file_id = doc.get("file_id")
        if not file_id:
            return
        self.documents[file_id] = doc
        
        # Index document-level metadata for facets
        self._index_facets(file_id, doc, level="document")

    def add_chunk(self, chunk: Dict[str, Any], vector: List[float] = None):
        """Adds a text chunk and its vector to the index."""
        chunk_id = chunk.get("chunk_id")
        if not chunk_id:
            return
        
        self.chunks[chunk_id] = chunk
        if vector:
            self.vectors[chunk_id] = np.array(vector) if HAS_NUMPY else vector
            
        # Update inverted index
        text = chunk.get("text_plain", "") or chunk.get("text", "")
        self._update_inverted_index(chunk_id, text)
        
        # Index chunk-level facets
        self._index_facets(chunk_id, chunk, level="chunk")

    def _update_inverted_index(self, doc_id: str, text: str):
        """Simple token-based inverted index update."""
        # Simple tokenization
        tokens = set(text.lower().split())
        for token in tokens:
            self.inverted_index[token].append(doc_id)

    def _index_facets(self, item_id: str, data: Dict[str, Any], level: str):
        """Updates faceted indexes."""
        # Configurable facets
        facets_to_index = ["jurisdiction", "clause_type", "tags", "file_id"]
        
        for field in facets_to_index:
            if field in data:
                value = data[field]
                if isinstance(value, list):
                    for v in value:
                        self.faceted_index[field][str(v)].append(item_id)
                else:
                    self.faceted_index[field][str(value)].append(item_id)

    def add_graph_node(self, node_id: str, node_type: str, metadata: Dict[str, Any]):
        """Adds a node to the entity graph."""
        self.graph["nodes"][node_id] = {
            "type": node_type,
            **metadata
        }

    def add_graph_edge(self, source: str, target: str, relation: str):
        """Adds an edge to the entity graph."""
        self.graph["edges"].append({
            "source": source,
            "target": target,
            "relation": relation
        })

    def search_hybrid(self, query: str, filters: Dict[str, Any] = None, k: int = 10, vector: List[float] = None) -> List[Dict[str, Any]]:
        """
        Performs a hybrid search combining keyword, vector, and filters.
        """
        # 1. Filter candidates
        candidates = set(self.chunks.keys())
        
        if filters:
            for field, value in filters.items():
                if field in self.faceted_index:
                    if field == "tags" and isinstance(value, list):
                         # Intersection for multiple tags? Or union? Let's do intersection for now
                         for tag in value:
                             candidates &= set(self.faceted_index[field].get(tag, []))
                    else:
                        candidates &= set(self.faceted_index[field].get(str(value), []))
        
        # 2. Keyword Search (BM25-ish or simple boolean)
        keyword_matches = set()
        query_tokens = query.lower().split()
        for token in query_tokens:
            if token in self.inverted_index:
                 keyword_matches.update(self.inverted_index[token])
        
        # If no vector, rely on keywords + filters
        if not vector and not query:
            # Return all/random if no query? limited by k
            results = []
            for cid in list(candidates)[:k]:
                 results.append(self.chunks[cid])
            return results

        candidate_list = list(candidates)
        
        # 3. Vector Similarity
        scores = []
        if vector:
             q_vec = np.array(vector) if HAS_NUMPY else vector
             for cid in candidate_list:
                 if cid not in self.vectors:
                     continue
                 doc_vec = self.vectors[cid]
                 score = self._cosine_similarity(q_vec, doc_vec)
                 
                 # Boost by keyword match
                 if cid in keyword_matches:
                     score *= 1.2 # Simple boost
                 
                 scores.append((cid, score))
        else:
            # Rank strictly by keyword overlap if no vector
             for cid in candidate_list:
                 if cid in keyword_matches:
                     scores.append((cid, 1.0)) # Flat score for now

        scores.sort(key=lambda x: x[1], reverse=True)
        top_k = scores[:k]
        
        return [
            {
                **self.chunks[cid],
                "score": score
            }
            for cid, score in top_k
        ]

    def _cosine_similarity(self, v1, v2) -> float:
        if HAS_NUMPY:
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(np.dot(v1, v2) / (norm1 * norm2))
        else:
            # Pure python fallback
            dot = sum(a*b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a*a for a in v1))
            norm2 = math.sqrt(sum(b*b for b in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

    def save(self):
        """Saves the index to disk."""
        # Save Documents
        with open(os.path.join(self.index_dir, "fastmap_metadata.json"), "w") as f:
             json.dump({
                 "documents": self.documents,
                 # "chunks": self.chunks, # Might be too large for JSON, ideally DB
                 "graph": self.graph
             }, f, indent=2)
             
        # Save Vectors (Binary)
        if HAS_NUMPY:
            # Simple dict save for now, could be optimized
            np.savez(os.path.join(self.index_dir, "fastmap_vectors.npz"), **self.vectors)
        else:
            with open(os.path.join(self.index_dir, "fastmap_vectors.json"), "w") as f:
                json.dump(self.vectors, f)

        # Save Chunks separately if needed
        with open(os.path.join(self.index_dir, "chunks.json"), "w") as f:
             json.dump(self.chunks, f)

    def load(self):
        """Loads the index from disk."""
        meta_path = os.path.join(self.index_dir, "fastmap_metadata.json")
        chunks_path = os.path.join(self.index_dir, "chunks.json")
        vec_path = os.path.join(self.index_dir, "fastmap_vectors.npz")
        vec_json_path = os.path.join(self.index_dir, "fastmap_vectors.json")
        
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                data = json.load(f)
                self.documents = data.get("documents", {})
                self.graph = data.get("graph", {"nodes": {}, "edges": []})
        
        if os.path.exists(chunks_path):
            with open(chunks_path, "r") as f:
                self.chunks = json.load(f)
                # Rebuild inverted index and facets
                for cid, chunk in self.chunks.items():
                    text = chunk.get("text_plain", "")
                    self._update_inverted_index(cid, text)
                    self._index_facets(cid, chunk, level="chunk")
                    
        if HAS_NUMPY and os.path.exists(vec_path):
            loaded = np.load(vec_path)
            self.vectors = {k: loaded[k] for k in loaded.files}
        elif os.path.exists(vec_json_path):
            with open(vec_json_path, "r") as f:
                self.vectors = json.load(f)
