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
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.messages.ai import AIMessage
from DecisionServiceTools import initializeTools
import prompts
from langchain.memory import ConversationBufferWindowMemory
from langchain.globals import set_verbose, set_debug
from RuleService import RuleService

class RuleAIAgent2:

    def __init__(self, llm, ruleServices):
        self.llm = llm
        # Initialize decision-service tools
        tools = initializeTools(ruleServices=ruleServices)

        # Conversation memory (last 5 messages)
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,
            return_messages=True,
            output_key="output"
        )

        # Prompt template including required placeholders
        template = "\n\n".join([
            prompts.PREFIX_WITH_TOOLS,
            "{tools}",
            prompts.ORIGINAL_FORMAT_INSTRUCTIONS,
            "User Input: {input}",
            "{agent_scratchpad}",
            prompts.SUFFIX_WITH_TOOLS,
        ])
        prompt = PromptTemplate.from_template(template)

        # Create a structured-chat agent with tools and memory
        agent = create_structured_chat_agent(
            self.llm,
            tools,
            prompt=prompt
        )

        # Agent executor with valid early-stopping
        self.pm_agent = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            early_stopping_method="force",
            memory=memory
        )

    def processMessage(self, userInput: str) -> dict:
        """Invoke the agent and return a JSON‑serialisable dict.

        The caller (e.g. `app.py`) expects a mapping with keys
        `input` and `output`, **not** a raw JSON string.  We therefore
        normalise whatever the agent returns into one clean string and
        wrap it in a Python dict so the caller can safely access
        `res["output"]` without hitting `AttributeError`.
        """
        # --- Run the agent -------------------------------------------------
        response = self.pm_agent.invoke({"input": userInput})

        # --- Normalise the LLM response into a plain string ---------------
        if isinstance(response, AIMessage):
            raw_output = response.content
        elif isinstance(response, dict):
            # LangChain often wraps the final answer under the "output" key
            raw_output = response.get("output", str(response))
        else:
            raw_output = str(response)

        # --- Sanitize for downstream JSON serialisation -------------------
        # Escape problematic characters for JSON
        translation_table = str.maketrans({
            '"': r'\"',
            '\n': r' ',
            '\t': r' ',
            '\r': r' '
        })


        safe_output = raw_output.translate(translation_table)
        safe_input  = userInput.translate(translation_table)

        # --- Return **dict**, not string ----------------------------------
        return {"input": safe_input, "output": safe_output}
