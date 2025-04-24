#
#    Copyright 2024 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

import json
import os
import logging
from typing import List
from langchain_core.tools import tool

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
def configure_logger(log_level: str = None):
    """
    Configures and returns a logger for the application.
    
    Args:
        log_level (str): The desired logging level, e.g., 'DEBUG', 'INFO'. 
                         If not provided, it will be read from the environment variable LOG_LEVEL,
                         defaulting to 'INFO'.
    
    Returns:
        logger (logging.Logger): Configured logger instance.
    """
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("Utils")
    logger.debug("Logger configured with level: %s", log_level)
    return logger

# Initialize logger at module level.
logger = configure_logger()

# -----------------------------------------------------------------------------
# Utility Functions for Descriptor Management
# -----------------------------------------------------------------------------
def find_descriptors(subdirtosearch: str) -> List[str]:
    """
    Searches for descriptor directories within the base data directory.
    
    Args:
        subdirtosearch (str): The subdirectory name to search for (e.g., "tool_descriptors").
    
    Returns:
        List[str]: A list of full paths to directories that match the search criteria.
    """
    tool_descriptors = []
    base_path = os.getenv("DATADIR", "../data")
    logger.debug("Searching for descriptors under base_path: %s", base_path)
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == subdirtosearch:
                path_found = os.path.join(root, dir_name)
                logger.debug("Found descriptor directory: %s", path_found)
                tool_descriptors.append(path_found)
    if not tool_descriptors:
        logger.warning("No descriptor directories found for: %s", subdirtosearch)
    return tool_descriptors

# -----------------------------------------------------------------------------
# Utility Functions for Result Formatting
# -----------------------------------------------------------------------------
def format_response(user_input: str, output_text: str) -> str:
    """
    Formats the user input and output text into a JSON string, escaping any problematic characters.
    
    Args:
        user_input (str): The original input string.
        output_text (str): The resulting output string.
    
    Returns:
        str: A JSON string with keys "input" and "output".
    """
    translation_table = str.maketrans({
        '"': r'\"',
        '\n': r' ',
        '\t': r' ',
        '\r': r' '
    })
    formatted_input = user_input.translate(translation_table)
    formatted_output = output_text.translate(translation_table)
    formatted_json = f'{{ "input": "{formatted_input}", "output": "{formatted_output}" }}'
    logger.debug("Formatted response: %s", formatted_json)
    return formatted_json

# -----------------------------------------------------------------------------
# Additional Configuration Management Utilities
# -----------------------------------------------------------------------------
def get_env_variable(var_name: str, default: str = None) -> str:
    """
    Retrieves an environment variable, or returns the default value if not set.
    
    Args:
        var_name (str): The name of the environment variable to retrieve.
        default (str): The default value to return if the variable is not set.
    
    Returns:
        str: The value of the environment variable or the default.
    """
    value = os.getenv(var_name, default)
    if value is None:
        logger.warning("Environment variable '%s' not found and no default is provided.", var_name)
    else:
        logger.debug("Environment variable '%s' has value: %s", var_name, value)
    return value

# Example tool declaration using the @tool decorator.
@tool
def echo_tool(input: str) -> str:
    """
    A simple tool that echoes the input. Useful for testing purposes.
    
    Args:
        input (str): Input string.
    
    Returns:
        str: The same input string.
    """
    logger.info("echo_tool received input: %s", input)
    return input

# -----------------------------------------------------------------------------
# End of Utils Module
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Test logging and utilities.
    logger.info("Starting Utils module test.")
    
    # Test find_descriptors.
    desc_dirs = find_descriptors("tool_descriptors")
    logger.info("Found descriptor directories: %s", desc_dirs)
    
    # Test format_response.
    sample_input = "Test input with \"quotes\" and newlines\nin it."
    sample_output = "Test output with \ttabs and newlines\nin it."
    formatted = format_response(sample_input, sample_output)
    logger.info("Formatted response: %s", formatted)
    
    # Test get_env_variable.
    test_var = get_env_variable("TEST_ENV_VAR", "default_value")
    logger.info("TEST_ENV_VAR: %s", test_var)
