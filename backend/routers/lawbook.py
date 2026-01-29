from fastapi import APIRouter, HTTPException
from typing import List
import os
from pathlib import Path

router = APIRouter(prefix="/lawbook", tags=["lawbook"])

# Path to markdown laws directory
MARKDOWN_LAWS_DIR = Path(__file__).parent.parent / "data" / "markdown-laws"


@router.get("/")
async def list_laws():
    """
    List all available markdown law files.
    Returns a list of law metadata including id and title.
    """
    try:
        if not MARKDOWN_LAWS_DIR.exists():
            raise HTTPException(status_code=404, detail="Markdown laws directory not found")
        
        laws = []
        for file_path in MARKDOWN_LAWS_DIR.glob("*.md"):
            # Use filename without extension as id
            file_id = file_path.stem
            # Use filename as title (can be enhanced later)
            title = file_path.stem.replace("_", " ")
            
            laws.append({
                "id": file_id,
                "title": title,
                "filename": file_path.name
            })
        
        # Sort by filename for consistent ordering
        laws.sort(key=lambda x: x["filename"])
        
        return {"laws": laws}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing laws: {str(e)}")


@router.get("/{filename}")
async def get_law_content(filename: str):
    """
    Get the content of a specific markdown law file.
    
    Args:
        filename: The filename (with or without .md extension)
    
    Returns:
        The markdown content of the law file
    """
    try:
        # Ensure filename has .md extension
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = MARKDOWN_LAWS_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Law file '{filename}' not found")
        
        # Read the markdown content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "filename": filename,
            "content": content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading law file: {str(e)}")
