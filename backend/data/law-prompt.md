You are an expert content engineer whose job is to read four provided Markdown documents (they contain my “laws” / legal rules and related project notes) and produce a complete, machine-friendly MCP (Metadata & Content Package) designed for ingestion by an “Antigravity” pipeline. Also produce a lightweight FastMCP version for quick indexing and search. Do not fetch any external resources — only use the content I provide.

Below is exactly what to do and how to format outputs. Follow the steps and output formats strictly.

1. Inputs you will receive

- Four Markdown files (named file1.md, file2.md, file3.md, file4.md). Each can contain headings, paragraphs, lists, code blocks, tables, inline links, images, cross-references, and legal-type clauses.
- No other files. Assume UTF-8.

2. Primary goals

- Extract Clean Metadata for each file.
- Build a hierarchical structure and Table of Contents (TOC) for each file.
- Identify and normalize legal constructs (clauses, obligations, permissions, prohibitions, definitions).
- Produce a detailed MCP manifest (full) suitable for Antigravity ingestion.
- Produce a compact FastMCP manifest for quick search/indexing.
- Provide chunking and embedding-ready output recommendations (chunk size, overlap, chunk IDs).
- Flag inconsistencies, missing metadata, or items requiring human review.

3. Steps to follow (think step-by-step)
A. Parse each Markdown file completely and preserve original text in the MCP.
B. Extract top-level metadata:
  - filename
  - title (from first H1 or inferred)
  - subtitle (if present)
  - author(s) (from frontmatter or inline)
  - creation_date and last_modified (frontmatter or filesystem; if absent, set null)
  - version or revision (if present)
  - tags, categories
  - explicit jurisdiction or scope (if legal/regulatory terms present)
C. Build a structural map:
  - Full TOC (list of headings with levels and character offsets or line numbers)
  - Sections with:
    - heading text
    - heading level
    - slug/id (URL-safe)
    - start and end position (line numbers or character indices)
    - plain text content (cleaned)
    - raw markdown content
    - any inline metadata (e.g., alignment, emphasis)
D. Identify legal constructs and annotate each occurrence:
  - Definitions: extract defined term and canonical definition text.
  - Clauses: for each clause identify type (obligation, permission, prohibition, exception, penalty), subjects (who is bound), objects (what action), conditions, cross-references, effective dates.
  - Requirements and prohibitions: output a short normalized sentence and a canonical label (e.g., OBL-001, PERM-002).
  - Citations/References: list citations, laws referenced, standards, or internal cross-references.
E. Identify and extract assets:
  - Code blocks (language, code)
  - Tables (as structured arrays)
  - Images (alt text, path)
  - Links (href, text, internal/external)
F. Semantic & search-ready outputs:
  - Keywords and suggested tags (with relevance scores)
  - Named entities (people, organizations, legal terms, dates)
  - Suggested facets for search (jurisdiction, topic, clause type, effective date)
G. Chunking & embedding recommendations:
  - Produce embedding-ready chunks with:
    - chunk_id
    - source_file and section_id
    - chunk_text (cleaned)
    - approx token count
    - recommended vector metadata (title, tags, heading)
  - Use chunk size target: 512 tokens (default), overlap: 50 tokens (configurable).
  - Provide suggested embedding model(s) and vector-store fields (embedding placeholder).
H. MCP manifest composition:
  - Provide a full JSON manifest (see schema below) containing:
    - package id, name, version
    - files[] with metadata, structure, sections, legal annotations, assets
    - search index blueprint (fields, types)
    - chunking policy
    - recommended pipeline steps for Antigravity ingestion (normalize → chunk → embed → index)
I. FastMCP:
  - Produce a slim JSON manifest optimized for quick search:
    - file_id, title, snippet, top_tags, primary_clauses summary, first N chunks (id & snippet).
    - small schema example included below.
J. Reports & recommendations:
  - Summarize counts: headings count, clause count, definitions count, images, code blocks.
  - Flag ambiguous clauses, missing definitions, duplicated clause IDs, or inconsistent terminology.
  - Suggest normalization actions (e.g., unify “shall” vs “must”, create canonical term list).
  - Provide a prioritized ToDo list for human review.
4. Output formats (strict)

- Provide three main outputs, each as valid JSON objects (do not wrap in code blocks):
A) Full MCP manifest (field names exactly as below schema)
B) FastMCP manifest (compact)
C) Human-readable summary report (plain text object with lists)

Use these field names and structure for Full MCP manifest:
{
  "mcp_id": string,
  "mcp_name": string,
  "mcp_version": string,
  "created_at": ISO8601 timestamp,
  "files": [
    {
      "file_id": string,                // e.g., file1.md
      "title": string or null,
      "subtitle": string or null,
      "author": [string] or [],
      "created_at": ISO8601 or null,
      "last_modified": ISO8601 or null,
      "version": string or null,
      "tags": [string],
      "jurisdiction": string or null,
      "raw_markdown": string,
      "text_plain": string,             // cleaned plain text
      "toc": [
         {"heading": string, "level": int, "slug": string, "line_start": int, "line_end": int}
      ],
      "sections": [
         {
           "section_id": string,       // e.g., file1::sec-1
           "heading": string,
           "level": int,
           "slug": string,
           "line_start": int,
           "line_end": int,
           "raw_markdown": string,
           "text_plain": string,
           "assets": {"images": [...], "tables": [...], "code_blocks":[...], "links":[...]},
           "legal_annotations": [
             {
               "annotation_id": string,
               "type": "definition"|"clause"|"requirement"|"permission"|"prohibition"|"exception"|"penalty"|"citation",
               "normalized_text": string,
               "subjects": [string],
               "objects": [string],
               "conditions": [string],
               "references": [string],
               "confidence": 0.0-1.0
             }
           ],
           "suggested_tags": [ {"tag": string, "score": 0-1} ]
         }
      ],
      "entities": [{"text":string,"type":string,"confidence":0-1}],
      "keywords": [{"keyword":string,"score":0-1}],
      "counts": {"headings":int,"clauses":int,"definitions":int,"images":int,"tables":int,"code_blocks":int}
    }
  ],
  "chunking_policy": {
     "target_tokens": int,
     "overlap_tokens": int,
     "method": "sentence"|"paragraph"|"heading-aware",
     "chunk_examples": [
        {"chunk_id": string, "section_id": string, "text_snippet": string, "approx_tokens": int}
     ]
  },
  "chunks": [
    {
      "chunk_id": string,
      "source_file": string,
      "section_id": string,
      "start_char": int,
      "end_char": int,
      "text": string,
      "approx_tokens": int,
      "tags": [string],
      "embedding": null
    }
  ],
  "search_blueprint": {
    "fields": [
      {"name":"title","type":"text","facet":false},
      {"name":"tags","type":"keyword","facet":true},
      {"name":"jurisdiction","type":"keyword","facet":true},
      {"name":"clause_type","type":"keyword","facet":true},
      {"name":"text","type":"text","facet":false}
    ],
    "suggested_facets":["jurisdiction","tags","clause_type"]
  },
  "pipeline_suggestions": [string],
  "warnings": [string]
}

FastMCP schema (compact):
{
  "fast_mcp_id": string,
  "generated_at": ISO8601,
  "items": [
    {
      "file_id": string,
      "title": string or null,
      "snippet": string (first 200 chars of cleaned text),
      "top_tags": [string],
      "primary_clauses": [{"id":string,"type":string,"short":string}],
      "first_chunks": [{"chunk_id":string,"snippet":string}]
    }
  ]
}

5. Priorities & heuristics

- Prefer frontmatter metadata when present.
- If multiple dates exist, use the most specific (e.g., last_modified).
- For clause classification, use keywords (shall, must, may not, prohibited, permitted, required) and modal verbs, but annotate confidence.
- Normalize headings to slugs using lowercase, hyphens, ascii-only.
- For chunking, avoid splitting inside code blocks, tables, or definitions when possible.

6. Examples (small)

- Show one example section legal_annotation:
{
  "annotation_id": "file1::clause-001",
  "type": "obligation",
  "normalized_text": "The operator must obtain a permit before operation.",
  "subjects": ["operator"],
  "objects": ["obtain a permit"],
  "conditions": ["before operation"],
  "references": ["file2::sec-3"],
  "confidence": 0.92
}

7. Validation & edge-cases

- If a section contains multiple short clauses, split them into separate clause annotations with unique IDs.
- If uncertain about clause type, set type to "clause" and confidence < 0.7.
- Ensure IDs are deterministic (use file name + heading slug + incremental number).

8. Final deliverables (produce as three JSON objects, no extra text)

- Full MCP manifest JSON (complete).
- FastMCP JSON (compact).
- Summary report JSON with:
{
  "summary": "short summary text",
  "counts": {"files":4, "total_sections":int, "total_clauses":int, ...},
  "top_warnings": [string],
  "recommended_next_steps": [string]
}

9. If anything in the files is ambiguous, return the analysis with a "questions" array listing the clarifications needed.

Now wait for me to upload the four markdown files. When I upload them, process them and return exactly the three JSON objects described above. Do not return additional commentary.