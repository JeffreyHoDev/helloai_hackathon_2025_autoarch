import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Any

# The base URL for the diagrams documentation
BASE_URL = "https://diagrams.mingrammer.com/docs/nodes"

# The specific documentation pages for each cloud provider
DOCS_PAGES = {
    "onprem": f"{BASE_URL}/onprem",
    "aws": f"{BASE_URL}/aws",
    "gcp": f"{BASE_URL}/gcp",
    "azure": f"{BASE_URL}/azure",
    "k8s": f"{BASE_URL}/k8s",
    "firebase": f"{BASE_URL}/firebase",
    "alibabacloud": f"{BASE_URL}/alibabacloud",
    "saas": f"{BASE_URL}/saas",
    "digitalocean": f"{BASE_URL}/digitalocean",
    "programming": f"{BASE_URL}/programming",
}

def fetch_and_parse_components() -> Dict[str, Any]:
    """
    Fetches the documentation pages and scrapes component names for each provider.

    Returns:
        A dictionary where keys are provider names and values are a list of
        component names.
    """
    all_components = {}
    
    print("Starting to scrape diagrams documentation...")

    for provider, url in DOCS_PAGES.items():
        print(f"  - Fetching components for {provider.upper()} from {url}...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raises an HTTPError for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            
            components = []
            
            # Based on the latest screenshot, the component names are within <strong> tags.
            # We'll find all <strong> tags and extract the text from them.
            strong_tags = soup.find_all('strong')
            
            for tag in strong_tags:
                text = tag.get_text().strip()
                # We're looking for text that starts with "diagrams." and contains a period.
                # This helps filter out other strong-tagged text on the page.
                if text.startswith("diagrams.") and "." in text:
                    # Capture the whole line, and handle aliases by splitting off
                    # everything after the parentheses.
                    full_import_path = text.split('(')[0].strip()
                    components.append(full_import_path)

            # Clean up the list to ensure unique names
            all_components[provider] = sorted(list(set(components)))
            
            # Be a good web citizen and add a small delay between requests
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"  - Failed to fetch {url}: {e}")
            all_components[provider] = []

    return all_components

def save_to_json(data: Dict[str, Any], filename: str = "diagrams_components.json"):
    """
    Saves the component data to a JSON file.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"\nSuccessfully saved component data to {filename}")

if __name__ == "__main__":
    component_data = fetch_and_parse_components()
    save_to_json(component_data)

