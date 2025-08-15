import json
from typing import Dict, Any
from pathlib import Path

from typing import Optional
from google.genai import types
from google.adk.agents.callback_context import CallbackContext

def validate_diagrams_import(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Reads the 'diagrams_components.json' file and returns its contents.

    This tool is designed to be a data retriever for an agent, providing
    a consistent and reliable way to access the list of valid 'diagrams'
    components without performing live web crawling.

    Returns:
        A string status
    """
    # Get the directory of the current script file
    script_dir = Path(__file__).parent
    json_path = script_dir / "diagrams_components.json"

    try:
        with open(json_path, "r") as f:
            valid_components = json.load(f)
        callback_context.state["valid_components"] = valid_components
        return None
    except FileNotFoundError:
        print("Error: 'diagrams_components.json' not found. Please run the scraping script first.")
        return "Error: 'diagrams_components.json' not found. Please run the scraping script first."
    except json.JSONDecodeError:
        print("Error: Failed to parse 'diagrams_components.json'. Check file for corruption.")
        return "Error: Failed to parse 'diagrams_components.json'. Check file for corruption."
