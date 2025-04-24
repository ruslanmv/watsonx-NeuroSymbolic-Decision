"""
prompt_handler.py

Purpose:
---------
- Assemble context-rich prompts that integrate ontology information and model evaluations.
- Include functions such as handle_evaluation_with_ontology() and parse_response() for interactions with WatsonxLLM.
"""

import re
import json
from langchain.prompts import PromptTemplate

# ------------------------------------------------------------------------------
# Stub for WatsonxLLM invocation. In production, replace or import the appropriate function.
# ------------------------------------------------------------------------------
def ask_watsonx(prompt: str) -> str:
    """
    Stub function to simulate WatsonxLLM responses.
    Replace this stub with actual integration code to call WatsonxLLM.
    """
    # For demonstration purposes, return a dummy response following the expected format.
    return (
        "Statements: Example statement generated from the context.\n"
        "Logical statements: example_statement.generated(from_context)\n"
        "Explanation: This example is based on the provided ontology and evaluation feedback."
    )

# ------------------------------------------------------------------------------
# Function: parse_response
# ------------------------------------------------------------------------------
def parse_response(response: str):
    """
    Extracts the 'Statements' and 'Logical statements' sections from a WatsonxLLM response.
    The response is expected to be in a specific format:
    
    Statements:
    <statements content>
    
    Logical statements:
    <logical statements content>
    
    Args:
        response (str): Raw text response from WatsonxLLM.
        
    Returns:
        tuple: A tuple containing two lists:
            (extracted_statements, extracted_logical_statements)
    """
    # Initialize containers and control variables.
    extracted_statements = []
    extracted_logical_statements = []
    in_statements_section = False
    in_logical_section = False

    # Split response into individual lines.
    lines = response.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect section headers.
        if line.startswith("Statements:"):
            in_statements_section = True
            in_logical_section = False
            content = line[len("Statements:"):].strip()
            if content:
                extracted_statements.append(content)
            continue
        elif line.startswith("Logical statements:"):
            in_logical_section = True
            in_statements_section = False
            content = line[len("Logical statements:"):].strip()
            if content:
                extracted_logical_statements.append(content)
            continue

        # Append lines based on the active section.
        if in_statements_section:
            extracted_statements.append(line)
        elif in_logical_section:
            extracted_logical_statements.append(line)
    
    return extracted_statements, extracted_logical_statements

# ------------------------------------------------------------------------------
# Function: handle_evaluation_with_ontology
# ------------------------------------------------------------------------------
def handle_evaluation_with_ontology(user_input: str, statement: str, ontology_info: str, evaluation_results: str, is_true: bool) -> str:
    """
    Constructs a context-rich prompt by integrating the user input, ontology summary, and evaluation results.
    Depending on whether the logical evaluation is true or false, different prompt instructions are used.
    This prompt is then sent to WatsonxLLM for further elaboration.
    
    Args:
        user_input (str): The original natural language input from the user.
        statement (str): The logical statement derived from the input.
        ontology_info (str): A summary of the ontology's classes, individuals, and properties.
        evaluation_results (str): Model and ontology evaluation feedback.
        is_true (bool): Flag indicating if the evaluated logical statement is true.
    
    Returns:
        response (str): The raw response from WatsonxLLM.
    """
    
    # Build the context to be provided to the LLM.
    llm_context = f"""
User Input:
{user_input}

Ontology Information:
{ontology_info}

Evaluation Results:
{evaluation_results}

Statement:
{statement}
"""
    # Choose a prompt template based on the evaluation outcome.
    if is_true:
        prompt_template_text = """
You are a knowledgeable AI assistant with expertise in ontology-based reasoning.

The provided statement has been evaluated as TRUE.

Using the context below, please generate:
- Statements that directly answer the user's input.
- The corresponding Logical statements (format: subject.property(object)).
- A brief Explanation of your reasoning.

Context:
{context}

Please provide your answer in the following exact format (without extra commentary):

Statements:
<Your statements here>

Logical statements:
<Your logical statements here>

Explanation:
<Brief explanation>
"""
    else:
        prompt_template_text = """
You are a knowledgeable AI assistant with expertise in ontology-based reasoning.

The provided statement has been evaluated as FALSE.

Using the context below, please generate the correct statements and logical statements that address the user's input.
Also, provide a concise explanation.

Context:
{context}

Please provide your answer in the following exact format (without extra commentary):

Statements:
<Your corrected statements here>

Logical statements:
<Your corrected logical statements here>

Explanation:
<Brief explanation>
"""
    # Use LangChain's PromptTemplate to fill in the context.
    prompt_template = PromptTemplate(input_variables=["context"], template=prompt_template_text)
    filled_prompt = prompt_template.format(context=llm_context)
    
    # Optionally, you could log or print the filled prompt for debugging.
    # print("Filled Prompt:", filled_prompt)
    
    # Invoke WatsonxLLM with the assembled prompt.
    response = ask_watsonx(filled_prompt)
    return response

# ------------------------------------------------------------------------------
# Optional: JSON-formatted handler that returns a structured response.
# ------------------------------------------------------------------------------
def handle_evaluation_with_ontology_json(user_input: str, statement: str, ontology_info: str, evaluation_results: str, is_true: bool) -> str:
    """
    Variant of handle_evaluation_with_ontology() that processes the LLM response and returns
    a JSON string containing the extracted statements and logical statements.
    
    Args:
        user_input (str): The user’s natural language query.
        statement (str): The logical statement derived from the query.
        ontology_info (str): Summary information of the ontology.
        evaluation_results (str): Feedback on the logical evaluation.
        is_true (bool): True if the statement is evaluated as correct, False otherwise.
    
    Returns:
        output_json (str): A JSON string with keys 'statements' and 'details'.
    """
    response = handle_evaluation_with_ontology(user_input, statement, ontology_info, evaluation_results, is_true)
    extracted_statements, extracted_logical_statements = parse_response(response)
    statements_str = "\n".join(extracted_statements)
    logical_statements_str = "\n".join(extracted_logical_statements)
    output = {
        "statements": statements_str,
        "details": f"Logical Statements:\n{logical_statements_str}"
    }
    return json.dumps(output, indent=4)

# ------------------------------------------------------------------------------
# Main testing block (for stand-alone debugging).
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Sample test inputs:
    sample_user_input = "How does piston failure affect the oil engine performance?"
    sample_statement = "piston_1.CausesFailure(oil_engine_1)"
    sample_ontology_info = "Ontology: Engine classes (OilEngine, ElectricEngine), Components (Piston, OilPump, Battery, Motor), and relationships."
    sample_evaluation_results = "The statement is validated as TRUE because piston_1 indeed causes failure in oil_engine_1 based on defined ontology."
    
    # Test with a TRUE evaluation.
    print("----- Testing True Evaluation -----")
    sample_response_true = handle_evaluation_with_ontology(
        sample_user_input,
        sample_statement,
        sample_ontology_info,
        sample_evaluation_results,
        is_true=True
    )
    print("LLM Response (True Evaluation):")
    print(sample_response_true)
    
    # Test with a FALSE evaluation.
    print("\n----- Testing False Evaluation -----")
    sample_response_false = handle_evaluation_with_ontology(
        sample_user_input,
        sample_statement,
        sample_ontology_info,
        sample_evaluation_results,
        is_true=False
    )
    print("LLM Response (False Evaluation):")
    print(sample_response_false)
    
    # Test JSON output variant.
    print("\n----- Testing JSON-formatted Response -----")
    sample_json = handle_evaluation_with_ontology_json(
        sample_user_input,
        sample_statement,
        sample_ontology_info,
        sample_evaluation_results,
        is_true=True
    )
    print("JSON Output:")
    print(sample_json)
