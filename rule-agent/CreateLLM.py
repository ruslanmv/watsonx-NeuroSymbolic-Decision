#
#    Copyright 2024 IBM Corp.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
"""Factory that returns an LLM instance based on $LLM_TYPE."""
import os

from CreateLLMLocal import createLLMLocal
from CreateLLMWatson import createLLMWatson
from CreateLLMBAM    import createLLMBAM


def createLLM():
    """Return a langchain *Runnable* LLM according to $LLM_TYPE.

    Supported values (case-sensitive):

      * WATSONX  – IBM watsonx.ai (default)
      * LOCAL_OLLAMA – local Ollama server
      * BAM      – IBM Granite/BAM service
    """
    llm_type = os.getenv("LLM_TYPE", "WATSONX")

    if llm_type == "WATSONX":
        print("Using LLM Service: IBM watsonx.ai")
        return createLLMWatson()

    if llm_type == "LOCAL_OLLAMA":
        print("Using LLM Service: Ollama")
        return createLLMLocal()

    if llm_type == "BAM":
        print("Using LLM Service: IBM BAM")
        return createLLMBAM()

    # Any other value is invalid – fail fast.
    raise ValueError(
        
        f"Valid options are WATSONX, LOCAL_OLLAMA or BAM. Unsupported LLM_TYPE '{llm_type}'. "
    )
