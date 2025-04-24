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
import os
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.tools.render import ( render_text_description, render_text_description_and_args)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages.ai import AIMessage
from operator import itemgetter
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough
)
from CreateLLM import createLLM
import prompts
from DecisionServiceTools import initializeTools
from RuleService import RuleService

# Check for advanced (Neuro Symbolic) mode flag from an environment variable.
ADVANCED_MODE = os.getenv("USE_NEURO_SYMBOLIC", "0") == "1"

@tool
def converse(input: str) -> str:
    "Provide a natural language response using the user input."
    llm = createLLM()
    return llm.invoke(input)

class RuleAIAgent:
    def __init__(self, llm, ruleServices):
        self.llm = llm
        # Initialize declared tools.
        self.tools = initializeTools(ruleServices=ruleServices)
        self.tools.append(converse)
        self.rendered_tools = render_text_description(self.tools)
        self.system_prompt = "\n\n".join(
            [
                prompts.PREFIX_WITH_TOOLS,
                self.rendered_tools,
                prompts.SUFFIX_WITH_TOOLS
            ]
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )
        self.llm_with_tools_chain = self.prompt | self.llm | JsonOutputParser() | self.tool_chain
        self.llm_chain = RunnableParallel(
            {
                "tool_call_result": self.llm_with_tools_chain,
                "originalInput": RunnablePassthrough()
            }
        )
        self.chain = self.llm_chain | self.nlg
        self.fallbackPrompt = PromptTemplate.from_template(
            prompts.INSTRUCTIONS
        )
        ChatPromptTemplate.from_messages(
            [("system", self.system_prompt), ("user", "{input}")]
        )
        self.fallbackChain = self.fallbackPrompt | self.llm

        # Set mode based on the configuration flag.
        self.advanced_mode = ADVANCED_MODE
        if self.advanced_mode:
            # Import and initialize Neuro Symbolic components.
            from neuro_symbolic.ontology_engine import create_ontology, get_ontology_info
            from neuro_symbolic.ml_model import modelizer
            from neuro_symbolic.prompt_handler import handle_evaluation_with_ontology
            self.ontology = create_ontology()
            self.ontology_info = get_ontology_info(self.ontology)
            self.model, self.vectorizer = modelizer(self.ontology)
            self.ns_handle_eval = handle_evaluation_with_ontology
            print("Neuro Symbolic mode enabled.")
        else:
            print("Using original NL → JSON pipeline.")

    # Define the function which returns the chosen tool to be run in the chain.
    def tool_chain(self, model_output):
        # Construct a map of tool names to tool objects.
        tool_map = {tool.name: tool for tool in self.tools}
        if tool_map.get(model_output["name"]):
            chosen_tool = tool_map[model_output["name"]]
            return itemgetter("arguments") | chosen_tool
        else:
            print("Tool:", model_output["name"], "is not registered with the LLM")
            return None

    def nlg(self, s):
        if s['tool_call_result'] is None:
            return converse.invoke({'input': s['originalInput']['input']})
        else:
            nlg_prompt = ChatPromptTemplate.from_messages(
                [("system", prompts.NLG_SYSTEM_PROMPT), ("user", "{input}")]
            )
            nlgChain = nlg_prompt | self.llm
            return nlgChain.invoke({'input': s['originalInput']['input'], 'result': s['tool_call_result']})

    def processMessage(self, userInput: str) -> str:
        # Advanced Neuro Symbolic mode processing.
        if self.advanced_mode:
            try:
                # Import the conversion function.
                from neuro_symbolic.ml_model import convert_to_logical
                # Convert the user input to a logical form using the trained ML model.
                logical_form = convert_to_logical(userInput, self.model, self.vectorizer)
                # For demonstration, define evaluation feedback. In a full implementation this would be computed.
                evaluation_results = "The logical form was generated and validated using the ontology."
                # Assume the evaluation deems the logical form correct.
                is_true = True
                # Call the Neuro Symbolic prompt handler.
                response = self.ns_handle_eval(userInput, logical_form, self.ontology_info, evaluation_results, is_true)
                return response
            except Exception as e:
                print("An exception occurred in advanced mode:", e)
                # Fallback to the original pipeline if an error occurs.
        
        # Original pipeline processing.
        response = None
        try:
            response = self.chain.invoke({'input': userInput})
        except Exception as e:
            print("An exception was raised when invoking a chain with tools:", e)
        
        if response is None:
            response = self.fallbackChain.invoke({'input': userInput})
        
        textResponse = ""
        if isinstance(response, AIMessage):
            textResponse = response.content
        else:
            textResponse = response

        translation_table = str.maketrans({'"': r'\"', '\n': r' ', '\t': r' ', '\r': r' '})
        return '{ "input": "' + userInput.translate(translation_table) + '", "output": "' + textResponse.translate(translation_table) + '"}'
