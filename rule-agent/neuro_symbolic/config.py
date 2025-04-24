"""
config.py

Purpose:
---------
- Store configuration parameters and decoding settings (e.g., token limits, temperature, etc.) for the Neuro Symbolic Approach.
- Manage environment variables and API keys if needed.

This module loads environment variables from a .env file (if available) and defines a set of configuration
parameters that can be used throughout the Neuro Symbolic pipeline.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file (if it exists)
load_dotenv()

# Watsonx and API credentials (with defaults as placeholders)
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "your_default_api_key")
PROJECT_ID = os.getenv("PROJECT_ID", "your_default_project_id")
WATSONX_URL = os.getenv("WATSONX_URL", "https://api.watsonx.example.com")  # Replace with actual API URL if needed

# Neuro Symbolic Decoding Parameters (used by the language model)
DECODING_PARAMS = {
    "decoding_method": "sample",   # Decoding strategy (e.g., sample, beam search, etc.)
    "max_new_tokens": 4095,         # Maximum number of tokens to generate
    "min_new_tokens": 1,            # Minimum number of tokens to generate
    "temperature": 0.5,             # Sampling temperature for output variability
    "top_k": 50,                    # Top-K filtering parameter
    "top_p": 1,                     # Top-p (nucleus) filtering parameter
}

# Additional configuration settings (for example, the model identifier)
MODEL_ID = "meta-llama/llama-3-1-70b-instruct"  # This is an example; update as needed

# Optional: You can define a configuration class to neatly encapsulate all these settings.
class NeuroSymbolicConfig:
    """
    A configuration class for holding all settings related to the Neuro Symbolic Approach.
    """
    def __init__(self):
        self.watsonx_api_key = WATSONX_API_KEY
        self.project_id = PROJECT_ID
        self.watsonx_url = WATSONX_URL
        self.decoding_params = DECODING_PARAMS
        self.model_id = MODEL_ID

    def __str__(self):
        return (
            f"NeuroSymbolicConfig(\n"
            f"  watsonx_api_key={self.watsonx_api_key},\n"
            f"  project_id={self.project_id},\n"
            f"  watsonx_url={self.watsonx_url},\n"
            f"  decoding_params={self.decoding_params},\n"
            f"  model_id={self.model_id}\n"
            f")"
        )

# Instantiate the configuration so it can be imported in other modules
CONFIG = NeuroSymbolicConfig()

# If this module is run directly, print out the configuration for debugging.
if __name__ == "__main__":
    print("Neuro Symbolic Configuration:")
    print(CONFIG)
