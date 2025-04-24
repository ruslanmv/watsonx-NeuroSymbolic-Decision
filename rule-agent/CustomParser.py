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
from langchain_core.exceptions import OutputParserException
from langchain.agents import AgentOutputParser
from typing import Union
from langchain.schema import AgentAction, AgentFinish
import re
import json
from langchain.output_parsers.json import parse_json_markdown
from prompts import FORMAT_INSTRUCTIONS

class CustomParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def normalize_logical_form(self, text: str) -> Union[str, None]:
        """
        Attempts to detect and normalize a logical form in the text.
        Recognizes patterns like 'piston_1.CausesFailure(oil_engine_1)' or
        'not battery_1.CausesFailure(oil_engine_1)'.
        Returns the normalized logical form if the pattern is recognized, else None.
        """
        pattern = r'^(not\s+)?(\w+)\.(\w+)\((\w+)\)$'
        match = re.match(pattern, text.strip())
        if match:
            negation = match.group(1) or ""
            subject = match.group(2)
            prop = match.group(3)
            obj = match.group(4)
            # Normalize: strip extra whitespace and ensure a consistent pattern.
            normalized = f"{negation.strip()} {subject.strip()}.{prop.strip()}({obj.strip()})".strip()
            normalized = re.sub(r'\s+', ' ', normalized)
            return normalized
        return None

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        try:
            # Attempt to parse the text as JSON using LangChain's helper.
            response = parse_json_markdown(text)
            action = response.get("action")
            action_input = response.get("action_input", "")
            if action == "Final Answer":
                if isinstance(action_input, dict):
                    if 'answer' in action_input:
                        action_input = action_input['answer']
                    elif 'response' in action_input:
                        action_input = action_input['response']
                    else:
                        action_input = str(action_input)
                return AgentFinish({"output": action_input}, text)
            else:
                return AgentAction(action, action_input, text)
        except Exception as e:
            print(f"JSON parsing failed with error: {e}")
            # If the JSON parsing fails, attempt to normalize the output as a logical form.
            normalized = self.normalize_logical_form(text)
            if normalized is not None:
                # Return the normalized logical form as a finished output.
                return AgentFinish({"output": normalized}, text)
            # Fallback: Return the raw text output.
            return AgentFinish({"output": text}, text)

    @property
    def _type(self) -> str:
        return "conversational_chat"
