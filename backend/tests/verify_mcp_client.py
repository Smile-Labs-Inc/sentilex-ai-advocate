
import sys
import os
import logging

# Connect to backend root which is the current directory
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mcp_client():
    try:
        from mcp_client import get_mcp_client, MCPClient
    except ImportError:
        # Try import as if we are outside
        from backend.mcp_client import get_mcp_client, MCPClient
    
    logger.info("Initializing MCP Client...")
    client = get_mcp_client()
    
    logger.info("Running Health Check...")
    is_healthy = client.health_check()
    logger.info(f"Health Check Result: {is_healthy}")
    
    if is_healthy:
        logger.info("Running Query Test...")
        try:
            results = client.query_legal_sources("data protection", max_sources=3)
            logger.info(f"Query returned {len(results)} sources.")
            for i, source in enumerate(results):
                logger.info(f"--- Source {i+1} ---")
                logger.info(f"Law: {source.law_name}")
                logger.info(f"Section: {source.section}")
                logger.info(f"Text Snippet: {source.text[:50]}...")
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    else:
        logger.warning("Skipping query test due to health check failure (expected if index is empty).")

if __name__ == "__main__":
    test_mcp_client()
