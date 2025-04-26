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
"""NL-to-tool-execution agent built on LangChain."""
from __future__ import annotations

import os
from operator import itemgetter
from typing import Any

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages.ai import AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
)

import prompts
from DecisionServiceTools import initializeTools
from CreateLLM import createLLM  # only for the fallback 'converse' tool

# Neuro-symbolic mode flag
ADVANCED_MODE = os.getenv("USE_NEURO_SYMBOLIC", "0") == "1"


@tool
def converse(input: str) -> str:
    """Fallback NL response using the underlying LLM."""
    llm_local = createLLM()
    return llm_local.invoke(input)


class RuleAIAgent:
    """Tool-calling agent with an optional neuro-symbolic path."""

    def __init__(self, llm: Any, ruleServices: dict[str, Any]) -> None:
        if llm is None:
            raise ValueError(
                "RuleAIAgent initialised with llm=None – "
                "ensure createLLM() succeeded and LLM_TYPE is valid."
            )

        # 1. Tools ----------------------------------------------------------------
        self.tools = initializeTools(ruleServices=ruleServices)
        self.tools.append(converse)
        rendered_tools = prompts.PREFIX_WITH_TOOLS + "\n\n" + \
            "\n\n".join(t.description for t in self.tools) + \
            "\n\n" + prompts.SUFFIX_WITH_TOOLS

        # 2. Prompts --------------------------------------------------------------
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", rendered_tools), ("user", "{input}")]
        )

        # 3. Chain: NL → JSON tool call ------------------------------------------
        self.llm_with_tools_chain = (
            self.prompt
            | llm
            | JsonOutputParser()
            | self._tool_chain
        )

        self._llm_chain = RunnableParallel(
            {
                "tool_call_result": self.llm_with_tools_chain,
                "originalInput": RunnablePassthrough(),
            }
        )
        self.chain = self._llm_chain | self._nlg

        # 4. Fallback chain (plain NL) -------------------------------------------
        self.fallbackChain = (
            PromptTemplate.from_template(prompts.INSTRUCTIONS)
            | llm
        )

        # 5. Optional neuro-symbolic extras --------------------------------------
        self.advanced_mode = ADVANCED_MODE
        if self.advanced_mode:
            from neuro_symbolic.ontology_engine import (
                create_ontology,
                get_ontology_info,
            )
            from neuro_symbolic.ml_model import modelizer
            from neuro_symbolic.prompt_handler import handle_evaluation_with_ontology

            self.ontology = create_ontology()
            self.ontology_info = get_ontology_info(self.ontology)
            self.model, self.vectorizer = modelizer(self.ontology)
            self.ns_handle_eval = handle_evaluation_with_ontology
            print("⚡ Neuro-Symbolic mode enabled.")
        else:
            print("🔗 Using standard NL → JSON → tool pipeline.")

    # --------------------------------------------------------------------- helpers
    def _tool_chain(self, model_output: dict) -> Any:
        """Return the runnable for the tool the LLM selected."""
        tool_map = {t.name: t for t in self.tools}
        chosen = tool_map.get(model_output.get("name"))
        if chosen is None:
            print("Tool not registered:", model_output.get("name"))
            return None
        return itemgetter("arguments") | chosen

    def _nlg(self, s: dict) -> str | AIMessage:
        """Turn the raw tool call result into a final NL answer."""
        if s["tool_call_result"] is None:
            return converse.invoke({"input": s["originalInput"]["input"]})

        nlg_prompt = ChatPromptTemplate.from_messages(
            [("system", prompts.NLG_SYSTEM_PROMPT), ("user", "{input}")]
        )
        nlg_chain = nlg_prompt | createLLM()
        return nlg_chain.invoke(
            {
                "input": s["originalInput"]["input"],
                "result": s["tool_call_result"],
            }
        )

    # --------------------------------------------------------------------- public
    def processMessage(self, userInput: str) -> str:
        """Main entry – produce a JSON string with the answer."""
        if self.advanced_mode:
            try:
                from neuro_symbolic.ml_model import convert_to_logical

                logical_form = convert_to_logical(
                    userInput, self.model, self.vectorizer
                )
                evaluation_results = (
                    "The logical form was generated and validated with the ontology."
                )
                is_true = True
                return self.ns_handle_eval(
                    userInput,
                    logical_form,
                    self.ontology_info,
                    evaluation_results,
                    is_true,
                )
            except Exception as exc:  # noqa: BLE001
                print("⚠️  Advanced mode failed:", exc)
                # fall back to standard pipeline

        try:
            response = self.chain.invoke({"input": userInput})
        except Exception as exc:  # noqa: BLE001
            print("⚠️  Tool pipeline failed:", exc)
            response = self.fallbackChain.invoke({"input": userInput})

        # Marshal to plain text for the REST caller
        if isinstance(response, AIMessage):
            response_text = response.content
        else:
            response_text = str(response)

        esc = str.maketrans({'"': r"\"", "\n": " ", "\t": " ", "\r": " "})
        return (
            '{ "input": "' + userInput.translate(esc) +
            '", "output": "' + response_text.translate(esc) + '"}'
        )
