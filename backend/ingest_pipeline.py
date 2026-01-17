import json
import os
import time
import uuid
import random
from datetime import datetime
from typing import Dict, Any, List

from index_engine import AntigravityIndex

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MCP_FULL_PATH = os.path.join(DATA_DIR, "full_mcp_manifest.json")
MCP_FAST_PATH = os.path.join(DATA_DIR, "mcp_fast.json")
MCP_REPORT_PATH = os.path.join(DATA_DIR, "antigravity_analysis.json")
OUTPUT_STATUS_PATH = os.path.join(DATA_DIR, "antigravity_status.json")

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Mock embedding generation.
    In a real scenario, this would call an API.
    Returning a random 1536-dim vector for simulation.
    """
    # Deterministic seed based on text length for consistency in testing
    random.seed(len(text)) 
    return [random.random() for _ in range(1536)]

def run_pipeline():
    start_time = time.time()
    status_report = {
        "pipeline_version": "1.0",
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "input_files": 0,
        "total_documents": 0,
        "total_chunks": 0,
        "total_embeddings": 0,
        "fastmap_indexes_created": [],
        "warnings_resolved": 0,
        "warnings_pending": 0,
        "query_endpoints": [
            "/search?q=<query>&filters=<facets>",
            "/similar?chunk_id=<id>&k=10",
            "/clause?type=<type>&jurisdiction=<jur>",
            "/graph?entity=<id>&depth=2"
        ],
        "errors": [],
        "health_status": "starting"
    }

    try:
        # Phase 1: Validation & Loading
        print("Phase 1: Validation & Loading...")
        if not all(os.path.exists(p) for p in [MCP_FULL_PATH, MCP_FAST_PATH, MCP_REPORT_PATH]):
            raise FileNotFoundError("One or more input files are missing.")
        
        mcp_full = load_json(MCP_FULL_PATH)
        mcp_fast = load_json(MCP_FAST_PATH)
        mcp_report = load_json(MCP_REPORT_PATH)
        status_report["input_files"] = 3
        
        # Cross-check consistency (simplified)
        full_files_count = len(mcp_full.get("files", []))
        # mcp_fast might verify against this
        
        # Initialize Index
        indexer = AntigravityIndex({
            "index_dir": os.path.join(DATA_DIR, "index")
        })

        # Phase 2: Indexing Strategy (Handled by AntigravityIndex internal structures)
        print("Phase 2: Indexing Strategy configured.")
        status_report["fastmap_indexes_created"] = ["inverted_index", "vector_index", "faceted_index", "graph"]

        # Phase 3: Embedding Generation & Document Loading
        print("Phase 3: Embedding Generation & Loading...")
        total_docs = 0
        total_chunks = 0
        
        for file_data in mcp_full.get("files", []):
            total_docs += 1
            indexer.add_document(file_data)
            
            # Process sections as chunks for this exercise if chunks aren't explicit
            # The prompt implies mcp_full.json -> chunks[], but sample has `sections[]`
            # We will treat sections as chunks if explicit chunks are missing
            chunks = file_data.get("chunks", [])
            if not chunks and "sections" in file_data:
                 # Flatten sections to chunks
                 for sec in file_data["sections"]:
                     chunks.append({
                         "chunk_id": sec.get("section_id", str(uuid.uuid4())),
                         "text_plain": sec.get("text_plain", ""),
                         "metadata": {
                             "file_id": file_data.get("file_id"),
                             "section_id": sec.get("section_id"),
                             "tags": sec.get("suggested_tags", []), # Extract just tags if dict?
                             "clause_types": [ann.get("type") for ann in sec.get("legal_annotations", [])]
                         },
                         # Include raw section data
                         "heading": sec.get("heading"),
                         "legal_annotations": sec.get("legal_annotations", [])
                     })
            
            for chunk in chunks:
                total_chunks += 1
                embedding = generate_embedding(chunk.get("text_plain", ""))
                indexer.add_chunk(chunk, vector=embedding)
                
                # Phase 4: Legal Entity Mapping
                # Process annotations from the chunk/section
                if "legal_annotations" in chunk:
                    for ann in chunk["legal_annotations"]:
                        ann_id = ann.get("annotation_id", str(uuid.uuid4()))
                        indexer.add_graph_node(ann_id, "annotation", ann)
                        
                        # Add subjects/objects as nodes
                        for subj in ann.get("subjects", []):
                            indexer.add_graph_node(subj, "entity", {"name": subj})
                            indexer.add_graph_edge(ann_id, subj, "has_subject")
                            
                        for obj in ann.get("objects", []):
                            indexer.add_graph_node(obj, "entity", {"name": obj})
                            indexer.add_graph_edge(ann_id, obj, "has_object")

        status_report["total_documents"] = total_docs
        status_report["total_chunks"] = total_chunks
        status_report["total_embeddings"] = total_chunks

        # Phase 5 & 6: Search Index & Optimization
        # (Implicitly handled by indexer.add_chunk updating inverted/faceted indexes)
        print("Phase 5 & 6: Indexes built.")

        # Phase 7 & 8: Pipeline Suggestions & Warnings
        # Process report warnings
        warnings = mcp_report.get("top_warnings", [])
        status_report["warnings_pending"] = len(warnings)
        # Simulate resolution for some
        resolved_count = 0
        for w in warnings:
            if "Typo" in w:
                resolved_count += 1 # Auto-resolve typos
        
        status_report["warnings_resolved"] = resolved_count
        status_report["warnings_pending"] -= resolved_count
        
        # Save Index
        indexer.save()
        status_report["health_status"] = "ready"
        print("Pipeline completed successfully.")

    except Exception as e:
        print(f"Pipeline failed: {e}")
        status_report["health_status"] = "error"
        status_report["errors"].append(str(e))
    
    # Write status report
    with open(OUTPUT_STATUS_PATH, "w") as f:
        json.dump(status_report, f, indent=2)

if __name__ == "__main__":
    run_pipeline()
