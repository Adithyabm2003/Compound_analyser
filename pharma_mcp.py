import json
import os
import logging
from mcp.server.fastmcp import FastMCP

# Configure logging (Errors only to protect the stdio channel)
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

# Initialize FastMCP Server
mcp = FastMCP("PharmaClinicalData")

# Relative path to the data file
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "clinical_db.json")

def load_clinical_database() -> dict:
    """Helper function to load the JSON database from disk securely."""
    if not os.path.exists(DB_FILE_PATH):
        logging.error(f"Database file missing at path: {DB_FILE_PATH}")
        return {}
    
    try:
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as je:
        logging.error(f"Malformed JSON data structure: {je}")
        return {}
    except Exception as e:
        logging.error(f"Unexpected file read error: {e}")
        return {}

@mcp.tool()
def get_compound_data(compound_name: str) -> str:
    """
    Retrieve pharmacological and clinical trial data for a specific compound.
    
    Args:
        compound_name: The name of the compound (e.g., 'compound-x9', 'pazopanib', 'imatinib')
    """
    # Normalize input for robust matching against keys
    name = compound_name.lower().strip()
    # Live load data file to ensure data freshness
    clinical_db = load_clinical_database()
    
    if not clinical_db:
        return "Error: Internal clinical data store is currently unavailable or corrupted."
        
    if name in clinical_db:
        return json.dumps(clinical_db[name], indent=2)
    
    # Handle missing compound entries gracefully for the LLM agent
    return (
        f"Error: Compound '{compound_name}' not found in the clinical database. "
        f"Available compounds are: {', '.join(clinical_db.keys())}."
    )

if __name__ == "__main__":
    # Standard stdio transport pipeline loop for execution
    mcp.run(transport='stdio')