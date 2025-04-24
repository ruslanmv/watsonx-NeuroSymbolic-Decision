"""
evaluation.py

Purpose:
---------
- Implement functions to check logical statements against the ontology 
  (e.g., check_statement_with_details(), evaluate_statements_with_details()).
- Generate human-readable evaluation feedback and explanations.
"""

import re
from owlready2 import *

def check_statement_with_details(onto, logical_statement: str):
    """
    Evaluates whether the given logical statement is true or false in the ontology and provides detailed feedback.

    The logical statement should be in the format: "subject.property(object)" or "not subject.property(object)".

    Args:
        onto: The loaded ontology (owlready2 ontology instance).
        logical_statement (str): The logical statement to evaluate.

    Returns:
        tuple(bool, str or None): A tuple where the first element is True if the statement evaluates
                                   as true (or false in the case of negation) and the second element is
                                   an explanation string if the evaluation fails (or None if it passes).
    """
    # Clean up and check for negation.
    ls = logical_statement.strip()
    is_negated = False
    if ls.lower().startswith("not "):
        is_negated = True
        ls = ls[4:].strip()

    # Expect format: subject.property(object)
    match = re.match(r"^(\w+)\.(\w+)\((\w+)\)$", ls)
    if not match:
        return False, "Logical statement format is incorrect. Expected format: subject.property(object)"
    
    subject_name, property_name, object_name = match.groups()
    
    # Look up elements in the ontology.
    subject = onto.search_one(iri="*#" + subject_name)
    obj = onto.search_one(iri="*#" + object_name)
    prop = onto.search_one(iri="*#" + property_name)
    
    if not subject:
        return False, f"Subject '{subject_name}' not found in the ontology."
    if not obj:
        return False, f"Object '{object_name}' not found in the ontology."
    if not prop:
        return False, f"Property '{property_name}' not found in the ontology."
    
    # Evaluate the relationship.
    holds = obj in prop[subject]
    # If the statement is negated, invert the result.
    if is_negated:
        holds = not holds

    if holds:
        return True, None
    else:
        if is_negated:
            explanation = (f"Evaluation failed: In the ontology, the relationship {subject_name}.{property_name}"
                           f"({object_name}) exists, contradicting the expected negation.")
        else:
            explanation = (f"Evaluation failed: In the ontology, the relationship {subject_name}.{property_name}"
                           f"({object_name}) does not hold as expected.")
        return False, explanation


def evaluate_statements_with_details(onto, statements):
    """
    Evaluates a list of logical statements against the ontology and collects details for each.

    Args:
        onto: The loaded ontology (owlready2 ontology instance).
        statements (List[str]): A list of logical statements (strings).

    Returns:
        tuple: A tuple containing:
            - true_statements (List[str]): Statements that evaluated as true.
            - false_statements (List[str]): Statements that evaluated as false.
            - details (dict): A mapping from false statements to their evaluation details.
    """
    true_statements = []
    false_statements = []
    details = {}

    for stmt in statements:
        result, detail = check_statement_with_details(onto, stmt)
        if result:
            true_statements.append(stmt)
        else:
            false_statements.append(stmt)
            details[stmt] = detail

    return true_statements, false_statements, details


def generate_evaluation_results(user_input: str, logical_form: str, evaluation_result: bool, details: str) -> str:
    """
    Generates a formatted summary of the evaluation results, including the user input,
    the produced logical form, and any evaluation feedback.

    Args:
        user_input (str): The original natural language input.
        logical_form (str): The logical form derived from the input.
        evaluation_result (bool): The result of the evaluation (True if the statement holds, False otherwise).
        details (str): Detailed explanation from the evaluation (if any).

    Returns:
        str: A formatted multi-line string summarizing the evaluation.
    """
    status = "TRUE" if evaluation_result else "FALSE"
    explanation = details if details else "No further explanation provided."
    result_summary = (
        f"Evaluation Results:\n"
        f"--------------------\n"
        f"User Input     : {user_input}\n"
        f"Logical Form   : {logical_form}\n"
        f"Evaluation     : {status}\n"
        f"Explanation    : {explanation}"
    )
    return result_summary


# Optionally, you can add more helper functions here for batch processing etc.

# -----------------------------------------------------------------------------
# Example Testing Block
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # For testing, load an ontology using the ontology engine.
    # This assumes that ontology_engine.create_ontology() is available.
    from neuro_symbolic.ontology_engine import create_ontology
    onto = create_ontology()

    # Test a single logical statement.
    test_statement = "piston_1.CausesFailure(oil_engine_1)"
    result, detail = check_statement_with_details(onto, test_statement)
    print("Test Statement:", test_statement)
    print("Evaluation Result:", result)
    print("Details:", detail)
    print()

    # Test evaluation on multiple statements.
    statements_to_test = [
        "piston_1.CausesFailure(oil_engine_1)",
        "battery_1.CausesFailure(oil_engine_1)",  # likely false if battery belongs to an electric engine
        "not motor_1.CausesFailure(electric_engine_1)"  # depends on ontology definition
    ]
    true_stmts, false_stmts, details_dict = evaluate_statements_with_details(onto, statements_to_test)
    print("True Statements:", true_stmts)
    print("False Statements:", false_stmts)
    print("Details for False Statements:", details_dict)
    print()

    # Generate a summary of the evaluation.
    summary = generate_evaluation_results("How does piston failure affect performance?",
                                          test_statement,
                                          result,
                                          detail)
    print("Evaluation Summary:")
    print(summary)
