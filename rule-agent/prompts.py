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

from langchain.agents.structured_chat.prompt import FORMAT_INSTRUCTIONS as BASE_FORMAT_INSTRUCTIONS

# --------------------------
# Original Prompt Templates
# --------------------------
PREFIX = """<s><<SYS>>Assistant is a expert JSON builder designed to assist with a wide range of tasks.
To answer the question of the user, the assistant can use tools. Tools available to Assistant are:
:<</SYS>>"""

ORIGINAL_FORMAT_INSTRUCTIONS = """RESPONSE FORMAT INSTRUCTIONS
----------------------------
When responding to me, please output a response in one of two formats:
**Option 1:**
Use this if you want the human to use a tool.
Markdown code snippet formatted in the following schema:
```json
{{{{
    "action": string, \\\\ The action to take. Must be one of {tool_names}
    "action_input": string \\\\ The input to the action
}}}} 
```
**Option #2:**
Use this if you want to respond directly to the human. Markdown code snippet formatted in the following schema:
```json
{{{{
    "action": "Final Answer",
    "action_input": string \\\\ You should put what you want to return to the user here in a human readable text.
}}}} 
```
"""

SUFFIX = """Begin! Remember, all actions must be formatted as markdown JSON strings.
  Question: {input}
  Thought:{agent_scratchpad}"""

PREFIX_WITH_TOOLS = """You are an assistant that has access to the following set of tools.
Here are the names and descriptions for each tool:"""

SUFFIX_WITH_TOOLS = """Given the user input, return the name and input of the tool to use.
The tool you return needs to be one from the list.
Return your response as a JSON blob with 'name' and 'arguments' keys.
The value associated with the 'arguments' key should be a dictionary of parameters.
Please format dates as 'yyyy-mm-dd'.
Return the JSON blob only. Don't provide explanation.
"""

NLG_SYSTEM_PROMPT = """
The user input contains a question for which the response is: {result}.
Generate the simplest sentence using this response. Don't provide any explanation.
For example, if the question is "what is the price of a pair of shoes" and the response is "$89", then generate: "the price of a pair of shoes is $89.".
Don't use the user input. Generate one sentence.
"""

INSTRUCTIONS_WITH_CONTEXT = """
<s> [INST] You are an assistant for question-answering tasks. Use the following pieces of retrieved context 
to answer the question. If you don't know the answer, just say that you don't know. Use three sentences
maximum and keep the answer concise and limited to the response to the question. [/INST] </s>
[INST] Question: {input}
Context: {context}
Answer: [/INST]
"""

INSTRUCTIONS = """
<s> [INST] You are an assistant for question-answering tasks. If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise and limited to the response to the question. [/INST] </s>
[INST] Question: {input}
Answer: [/INST]
"""

# -----------------------------------------------------
# New Enhanced Prompt Templates for Neuro Symbolic Workflow
# -----------------------------------------------------
# These templates provide instructions to the LLM that include ontology information and evaluation results.
ENHANCED_PROMPT_TRUE = """
You are a knowledgeable AI assistant with domain expertise and a deep understanding of the provided ontology.
The following context includes details of the ontology and evaluation results indicating that the logical statement is TRUE.

Ontology Information:
{ontology_info}

Evaluation Results:
{evaluation_results}

User Input:
{input}

Task:
Based solely on the above context, generate:
- A brief Statement that directly answers the user's query.
- The corresponding Logical statement in the format: subject.property(object)
- A concise Explanation (one sentence) justifying your answer.

Please provide your answer in the following exact format (without extra commentary):

Statements:
<Your answer statement here>

Logical statements:
<Your logical statement here>

Explanation:
<Your brief explanation here>
"""

ENHANCED_PROMPT_FALSE = """
You are a knowledgeable AI assistant with domain expertise and a deep understanding of the provided ontology.
The following context includes details of the ontology and evaluation results indicating that the original logical statement is FALSE.

Ontology Information:
{ontology_info}

Evaluation Results:
{evaluation_results}

User Input:
{input}

Task:
Based solely on the above context, generate:
- A revised Statement that correctly answers the user's query.
- The corresponding corrected Logical statement in the format: subject.property(object)
- A concise Explanation (one sentence) justifying your revised answer.

Please provide your answer in the following exact format (without extra commentary):

Statements:
<Your revised answer statement here>

Logical statements:
<Your corrected logical statement here>

Explanation:
<Your brief explanation here>
"""

ENHANCED_PROMPT_GENERAL = """
You are a knowledgeable AI assistant with domain expertise and a comprehensive understanding of the provided ontology and reasoning results.

Ontology Information:
{ontology_info}

Evaluation Results:
{evaluation_results}

User Input:
{input}

Task:
Using the above context, provide a clear and concise answer that includes:
- A Statement that directly responds to the user.
- The corresponding Logical statement (formatted as subject.property(object)).
- A short Explanation outlining your reasoning.

Please format your response as follows:

Statements:
<Your answer statement>

Logical statements:
<Your logical statement>

Explanation:
<Your explanation>
"""

# Expose the enhanced templates so that other modules can import and use them.
# They can be used by functions in the neuro symbolic prompt handlers or agent configurations.
__all__ = [
    "PREFIX",
    "ORIGINAL_FORMAT_INSTRUCTIONS",
    "SUFFIX",
    "PREFIX_WITH_TOOLS",
    "SUFFIX_WITH_TOOLS",
    "NLG_SYSTEM_PROMPT",
    "INSTRUCTIONS_WITH_CONTEXT",
    "INSTRUCTIONS",
    "ENHANCED_PROMPT_TRUE",
    "ENHANCED_PROMPT_FALSE",
    "ENHANCED_PROMPT_GENERAL",
    "BASE_FORMAT_INSTRUCTIONS",
]
