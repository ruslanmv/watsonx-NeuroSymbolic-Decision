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
from typing import List

from langchain_core.tools import tool
from langchain_core.tools import BaseTool
from langchain_community.llms import Ollama
from langchain_core.pydantic_v1 import BaseModel
from Utils import find_descriptors

from RuleService import RuleService

# Import neuro symbolic evaluation routine if available.
# This function is assumed to exist in the neuro_symbolic.evaluation module.
try:
    from neuro_symbolic.evaluation import evaluate_decision_logic
except ImportError:
    # If the module does not exist or cannot be imported, define a stub.
    def evaluate_decision_logic(rulesetPath, decisionInputs):
        print("Neuro Symbolic evaluation not available; falling back to standard decision logic.")
        return None

class ToolDescriptor(BaseModel):
    engine: str
    toolName: str
    toolDescription: str
    toolPath: str
    args: List[dict]
    output: str

def read_json_tool_descriptors(directory_path):
    """Reads all JSON files in a directory and returns a list of ToolDescriptor objects.

    :param directory_path: The path to the directory containing the JSON files.
    :return: A list of ToolDescriptor instances.
    """
    descriptors = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
                descriptors.append(ToolDescriptor(**data))
    return descriptors

def initToolDescription(toolDescriptor: ToolDescriptor):
    desc = toolDescriptor.toolDescription
    desc = desc + """
        Make sure you use a input format similar to the JSON below:
        {
    """
    first = True
    for tad in toolDescriptor.args:
        if first == False:
            desc = desc + ", "
        desc = desc + '"' + tad['argName'] + '": "' + tad['argDescription'] + '"'
        first = False
    desc = desc + "}"
    return desc

class GenericDecisionServiceTool(BaseTool):
    toolPath: str
    outputProperty: str
    executionService: RuleService
    # New attribute to control use of Neuro Symbolic evaluation
    use_neuro_symbolic: bool = False

    def _run(self, **kwargs) -> str:
        """Use the tool."""
        print("Use Decision Service: " + self.name + " with ", kwargs)
        
        if self.use_neuro_symbolic:
            # Invoke the Neuro Symbolic evaluation routine.
            decisionOutput = evaluate_decision_logic(rulesetPath=self.toolPath, decisionInputs=kwargs)
            print("Neuro Symbolic evaluation responded: ", decisionOutput)
        else:
            # Fallback to the standard decision service invocation.
            decisionOutput = self.executionService.invokeDecisionService(rulesetPath=self.toolPath, decisionInputs=kwargs)
            print("Decision service responded: ", decisionOutput)
        
        if decisionOutput is not None:
            return decisionOutput[self.outputProperty]
        return None
    
    async def _arun(self, query: str, description: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("API does not support async")

def initializeTools(ruleServices):
    """
    Initialize decision service tools based on JSON descriptors.
    Additionally, check for an environment variable 'USE_NEURO_SYMBOLIC'
    to optionally enable Neuro Symbolic evaluation routines for each tool.
    """
    res = []
    # Check an environment variable for neuro symbolic usage (default disabled)
    use_neuro_flag = os.getenv("USE_NEURO_SYMBOLIC", "0") == "1"

    tool_descriptors_dirs = find_descriptors('tool_descriptors')
    # For each directory containing tool descriptors:
    for directory in tool_descriptors_dirs:
        tools = read_json_tool_descriptors(directory)
        for t in tools:
            tool_instance = GenericDecisionServiceTool(
                executionService=ruleServices[t.engine],
                name=t.toolName,
                description=initToolDescription(t),
                toolPath=t.toolPath,
                outputProperty=t.output
            )
            # Set the neuro symbolic option according to the environment flag.
            tool_instance.use_neuro_symbolic = use_neuro_flag
            res.append(tool_instance)
    return res
