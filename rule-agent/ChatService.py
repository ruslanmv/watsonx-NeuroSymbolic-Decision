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
"""Flask front-end for the Rule-AI agent."""
import os
import json
from flask import Flask, request
from flask_cors import CORS

from CreateLLM import createLLM
from RuleAIAgent import RuleAIAgent
from AIAgent import AIAgent
from ODMService import ODMService
from ADSService import ADSService
from Utils import find_descriptors

# ─────────────────────────────────────────────────────────────────────────────
# Configuration ─ default to IBM watsonx.ai if LLM_TYPE is missing
# ─────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("LLM_TYPE", "WATSONX")

ROUTE = "/rule-agent"

# ─────────────────────────────────────────────────────────────────────────────
# Create back-end services first (ADS ⭢ ODM). Must come before get_rule_services.
# ─────────────────────────────────────────────────────────────────────────────
adsService = ADSService()
odmService = ODMService()


def get_rule_services() -> dict:
    """Return whichever decision service is reachable."""
    # Prefer ADS if it is up; otherwise fall back to ODM.
    return {"ads": adsService} if adsService.isConnected else {"odm": odmService}


ruleServices = get_rule_services()

# ─────────────────────────────────────────────────────────────────────────────
# LLM – fail fast if we cannot build one
# ─────────────────────────────────────────────────────────────────────────────
llm = createLLM()
if llm is None:
    raise RuntimeError(
        "createLLM() returned None – check environment variables required for "
        "the selected LLM_TYPE (currently '{}').".format(os.getenv("LLM_TYPE"))
    )

# ─────────────────────────────────────────────────────────────────────────────
# Agents
# ─────────────────────────────────────────────────────────────────────────────
ruleAIAgent = RuleAIAgent(llm, ruleServices)  # NL+tools
aiAgent = AIAgent(llm)                        # plain RAG

# ─────────────────────────────────────────────────────────────────────────────
# Flask app
# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


def _ingest_all_documents(directory_path: str) -> None:
    """Load every PDF in *directory_path* into the RAG vector store."""
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(directory_path, filename)
            print("Ingesting document:", path)
            aiAgent.ingestDocument(path)


# Pre-load any PDF catalog documents
for catalog_dir in find_descriptors("catalog"):
    _ingest_all_documents(catalog_dir)

# ───────────────────── Flask routes ──────────────────────
@app.route(ROUTE + "/chat_with_tools", methods=["GET"])
def chat_with_tools():
    if not odmService.isConnected:
        return {"output": "Not connected to any Decision runtime", "type": "error"}

    user_input = request.args.get("userMessage", "")
    print("chat_with_tools received:", user_input)
    return ruleAIAgent.processMessage(user_input)


@app.route(ROUTE + "/chat_without_tools", methods=["GET"])
def chat_without_tools():
    user_input = request.args.get("userMessage", "")
    print("chat_without_tools received:", user_input)
    return aiAgent.processMessage(user_input)


print("✅  Chat service is ready on route", ROUTE)

if __name__ == "__main__":
    # NOTE: use environment variables (e.g. FLASK_RUN_PORT) for production
    app.run(debug=True)
